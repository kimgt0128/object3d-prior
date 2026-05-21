"""프레임 소스 추상화.

다양한 입력(합성 numpy 배열, 영상 파일)을 공통 인터페이스로 노출한다.
각 소스는 ``(index, timestamp_s, frame_ndarray)`` 튜플을 순서대로 yield한다.

cv2(opencv-python)는 선택 의존성이다. ``VideoFrameSource`` 내부에서만
lazy import하므로 cv2가 없어도 이 모듈 import는 깨지지 않는다.
"""

from __future__ import annotations

import abc
from typing import Iterator, List, Sequence, Tuple

import numpy as np

# (원본 인덱스, 타임스탬프(초), 프레임 배열)
FrameTuple = Tuple[int, float, np.ndarray]


class FrameSource(abc.ABC):
    """프레임 소스 추상 베이스.

    구현체는 ``source_fps``를 노출하고, ``iter_frames``로 원본 프레임을
    순서대로 yield해야 한다.

    ``__len__``은 전체 프레임 수를 알 때만 정수를 반환한다. 알 수 없으면
    ``TypeError``를 던져야 한다. 길이가 불확실한데 0을 조용히 반환하면
    다운스트림이 빈 매니페스트를 만들 수 있으므로 금지한다. 따라서
    파이프라인은 길이에 의존하지 말고 ``iter_frames``를 스트리밍해야 한다.
    """

    source_fps: float

    @abc.abstractmethod
    def iter_frames(self) -> Iterator[FrameTuple]:
        """원본 프레임을 ``(index, timestamp_s, frame)`` 순서로 yield한다."""
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        """전체 프레임 수.

        Raises:
            TypeError: 전체 프레임 수를 알 수 없을 때.
        """
        raise NotImplementedError


class ArrayFrameSource(FrameSource):
    """메모리 내 numpy 배열 기반 합성 프레임 소스.

    테스트에서 실제 영상 파일이나 cv2 없이 파이프라인을 검증하는 데 쓴다.
    """

    def __init__(self, frames: Sequence[np.ndarray], source_fps: float) -> None:
        if source_fps <= 0:
            raise ValueError(f"source_fps must be positive, got {source_fps}")
        self._frames: List[np.ndarray] = list(frames)
        self.source_fps = float(source_fps)

    def iter_frames(self) -> Iterator[FrameTuple]:
        for index, frame in enumerate(self._frames):
            timestamp_s = index / self.source_fps
            yield index, timestamp_s, frame

    def __len__(self) -> int:
        return len(self._frames)


class VideoFrameSource(FrameSource):
    """cv2 기반 영상 파일 프레임 소스.

    cv2는 생성자 안에서 lazy import한다. 모듈 import 시점에 cv2가 없어도
    되며, 실제로 영상 소스를 쓸 때만 의존성이 요구된다.
    """

    def __init__(self, video_path: str) -> None:
        try:
            import cv2  # noqa: F401  (lazy optional dependency)
        except ImportError as exc:  # pragma: no cover - 환경 의존
            raise ImportError(
                "VideoFrameSource requires opencv-python (cv2). "
                "Install it with `pip install opencv-python`."
            ) from exc

        self._cv2 = cv2
        self.video_path = str(video_path)

        capture = cv2.VideoCapture(self.video_path)
        if not capture.isOpened():  # pragma: no cover - 환경 의존
            capture.release()
            raise FileNotFoundError(f"cannot open video: {self.video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        capture.release()

        if not fps or fps <= 0:  # pragma: no cover - 환경 의존
            raise ValueError(f"invalid source fps reported by video: {fps}")

        self.source_fps = float(fps)
        # OpenCV가 CAP_PROP_FRAME_COUNT를 보고하지 못하면(가변 프레임레이트
        # mp4 등) 0을 신뢰하지 않고 None(=unknown)으로 둔다. 0을 그대로
        # 쓰면 다운스트림이 빈 매니페스트를 조용히 만든다(Bug 2).
        self._frame_count = (
            int(frame_count) if frame_count and frame_count > 0 else None
        )

    def iter_frames(self) -> Iterator[FrameTuple]:  # pragma: no cover - 환경 의존
        cv2 = self._cv2
        capture = cv2.VideoCapture(self.video_path)
        try:
            index = 0
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                # cv2는 BGR로 읽으므로 다운스트림 일관성을 위해 RGB로 변환.
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp_s = index / self.source_fps
                yield index, timestamp_s, frame_rgb
                index += 1
        finally:
            capture.release()

    def __len__(self) -> int:
        """전체 프레임 수. 알 수 없으면 TypeError를 던진다.

        OpenCV가 프레임 수를 보고하지 못한 경우 조용히 0을 반환하지 않는다.
        이는 빈 매니페스트가 정상인지 버그인지 구분할 수 없게 만들기
        때문이다. 파이프라인은 이 값에 의존하지 말고 스트리밍해야 한다.
        """
        if self._frame_count is None:
            raise TypeError(
                f"frame count is unknown for video: {self.video_path}. "
                "Stream frames via iter_frames() instead of relying on len()."
            )
        return self._frame_count
