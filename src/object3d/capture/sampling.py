"""프레임 샘플링 로직.

순수 로직만 둔다. 영상 I/O나 파일 저장과 분리해 단위 테스트가 쉽게 한다.

핵심 설계는 ``FrameSampler`` — 현재 인덱스와 내부 상태만으로 프레임을
유지할지 결정하는 스트리밍 keep predicate다. 전체 프레임 수가 필요 없어
가변 프레임레이트 영상처럼 길이를 모르는 소스도 안전하게 처리한다.

``compute_sample_indices``는 전체 프레임 수를 아는 경우의 편의 wrapper로,
내부적으로 ``FrameSampler``를 그대로 쓴다.
"""

from __future__ import annotations

import math
from typing import List


class FrameSampler:
    """rational(Bresenham 스타일) 다운샘플링 keep predicate.

    원본 fps를 target fps로 다운샘플링한다. 정수 step(``source_fps //
    target_fps``)은 비정수 비율에서 유효 fps를 크게 overshoot한다
    (예: 29.97fps -> 10fps 가 step 2로 유효 ~14.98fps). 대신 rational rule을
    쓴다.

    - ``r = target_fps / source_fps``
    - 프레임 ``i``(0-indexed)는 새 "target tick"에 도달할 때만 유지한다.
      즉 ``floor(i * r) > floor((i - 1) * r)``. 단, ``floor((-1) * r)``는
      ``-1``로 본다(프레임 0은 항상 유지).
    - ``target_fps >= source_fps``이면 업샘플링하지 않고 모든 프레임 유지.

    이 규칙은 정수/비정수 비율 모두에서 유효 fps가 target_fps에 수렴하며
    프레임 간격이 균등하다. ``ceil(source_fps / target_fps)`` 정수 step은
    비율이 정수 바로 위일 때(예: 25 -> 12fps) 심하게 under-sample하므로
    쓰지 않는다.

    스트리밍 keep predicate이므로 전체 프레임 수가 필요 없다.
    ``should_keep``은 단조 증가하는 인덱스로 호출되는 것을 가정하고
    마지막 tick만 내부 상태로 추적한다.
    """

    def __init__(self, source_fps: float, target_fps: float) -> None:
        if source_fps <= 0:
            raise ValueError(f"source_fps must be positive, got {source_fps}")
        if target_fps <= 0:
            raise ValueError(f"target_fps must be positive, got {target_fps}")

        self.source_fps = float(source_fps)
        self.target_fps = float(target_fps)
        # target >= source 이면 업샘플링 불가 -> 전 프레임 유지.
        self._keep_all = self.target_fps >= self.source_fps
        self._ratio = self.target_fps / self.source_fps
        # floor((-1) * r) == -1 로 초기화해 인덱스 0이 항상 유지되게 한다.
        self._last_tick = -1

    def should_keep(self, index: int) -> bool:
        """원본 프레임 ``index``를 유지해야 하면 True.

        ``index``는 0부터 단조 증가하는 순서로 호출되어야 한다.
        """
        if index < 0:
            raise ValueError(f"index must be non-negative, got {index}")
        if self._keep_all:
            return True
        tick = math.floor(index * self._ratio)
        if tick > self._last_tick:
            self._last_tick = tick
            return True
        return False


def compute_sample_indices(
    total_frames: int,
    source_fps: float,
    target_fps: float,
) -> List[int]:
    """원본 프레임 중 유지할 인덱스 목록을 계산한다.

    전체 프레임 수를 아는 경우의 편의 wrapper다. ``FrameSampler``의
    rational rule을 그대로 적용한다.

    Args:
        total_frames: 원본 영상의 전체 프레임 수.
        source_fps: 원본 영상의 초당 프레임 수.
        target_fps: 원하는 초당 프레임 수.

    Returns:
        유지할 원본 프레임 인덱스의 오름차순 리스트.

    Raises:
        ValueError: fps가 양수가 아니거나 total_frames가 음수일 때.
    """
    if total_frames < 0:
        raise ValueError(f"total_frames must be non-negative, got {total_frames}")

    # fps 유효성 검증은 FrameSampler 생성자에 위임한다.
    sampler = FrameSampler(source_fps=source_fps, target_fps=target_fps)
    return [i for i in range(total_frames) if sampler.should_keep(i)]
