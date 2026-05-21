"""run_capture 파이프라인 스모크 테스트 (ArrayFrameSource + tmp_path)."""

from typing import Iterator

import numpy as np
import pytest

from object3d.capture.frame_source import ArrayFrameSource, FrameSource, FrameTuple
from object3d.capture.manifest import read_manifest
from object3d.capture.pipeline import run_capture
from object3d.capture.records import CaptureMetadata


def _make_frames(n, height=8, width=8):
    # 결정적 합성 프레임: 각 프레임은 인덱스 값으로 채운 단색 RGB
    rng = np.arange(n)
    return [
        np.full((height, width, 3), fill_value=int(i % 256), dtype=np.uint8)
        for i in rng
    ]


def _metadata():
    return CaptureMetadata(
        object_name="cardboard_box",
        measured_cm={"width": 30.0, "depth": 20.0, "height": 15.0},
        camera_mode="handheld",
        lighting="indoor_diffuse",
        material="cardboard",
        source_video="synthetic://array",
        source_fps=30.0,
    )


def _run(tmp_path, frames):
    source = ArrayFrameSource(frames, source_fps=30.0)
    output_dir = tmp_path / "frames"
    manifest_path = tmp_path / "manifest.json"
    return run_capture(
        source=source,
        metadata=_metadata(),
        target_fps=10.0,
        output_dir=output_dir,
        manifest_path=manifest_path,
    )


def test_pipeline_produces_expected_frame_count(tmp_path):
    frames = _make_frames(12)
    manifest = _run(tmp_path, frames)
    # 30fps -> 10fps, total 12 -> indices 0,3,6,9 -> 4 frames
    assert len(manifest["frames"]) == 4


def test_pipeline_saves_frame_files(tmp_path):
    frames = _make_frames(12)
    manifest = _run(tmp_path, frames)
    for record in manifest["frames"]:
        saved = tmp_path / record["image_path"]
        assert saved.exists(), f"missing frame file: {saved}"
        assert saved.stat().st_size > 0


def test_pipeline_frame_ids_and_timestamps(tmp_path):
    frames = _make_frames(12)
    manifest = _run(tmp_path, frames)
    ids = [r["frame_id"] for r in manifest["frames"]]
    assert ids == [0, 1, 2, 3]
    # source_index 0,3,6,9 at 30fps -> timestamps 0.0, 0.1, 0.2, 0.3
    timestamps = [r["timestamp_s"] for r in manifest["frames"]]
    assert timestamps == [0.0, 0.1, 0.2, 0.3]
    # camera_metadata는 원본 인덱스를 보존
    src_indices = [r["camera_metadata"]["source_index"] for r in manifest["frames"]]
    assert src_indices == [0, 3, 6, 9]


def test_pipeline_writes_manifest_file(tmp_path):
    frames = _make_frames(12)
    manifest = _run(tmp_path, frames)
    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.exists()
    loaded = read_manifest(manifest_path)
    assert loaded == manifest


def test_pipeline_is_reproducible(tmp_path):
    # 같은 입력 -> 동일한 manifest (image_path는 상대 경로라 디렉터리 무관)
    frames = _make_frames(12)
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    run_a.mkdir()
    run_b.mkdir()

    manifest_a = run_capture(
        source=ArrayFrameSource(_make_frames(12), source_fps=30.0),
        metadata=_metadata(),
        target_fps=10.0,
        output_dir=run_a / "frames",
        manifest_path=run_a / "manifest.json",
    )
    manifest_b = run_capture(
        source=ArrayFrameSource(_make_frames(12), source_fps=30.0),
        metadata=_metadata(),
        target_fps=10.0,
        output_dir=run_b / "frames",
        manifest_path=run_b / "manifest.json",
    )
    assert manifest_a == manifest_b


def test_pipeline_empty_source(tmp_path):
    # 진짜로 0프레임을 yield하는 소스는 빈 매니페스트가 정상.
    manifest = _run(tmp_path, [])
    assert manifest["frames"] == []


# --- Bug 2: 전체 프레임 수를 모르는 소스 ---


class UnknownLengthFrameSource(FrameSource):
    """전체 프레임 수를 알 수 없는 테스트용 소스.

    OpenCV가 CAP_PROP_FRAME_COUNT를 보고하지 못하는 가변 프레임레이트
    영상을 흉내낸다. ``__len__``은 TypeError를 던지지만 ``iter_frames``는
    N개의 합성 프레임을 정상적으로 yield한다.
    """

    def __init__(self, frames, source_fps: float) -> None:
        self._frames = list(frames)
        self.source_fps = float(source_fps)

    def iter_frames(self) -> Iterator[FrameTuple]:
        for index, frame in enumerate(self._frames):
            yield index, index / self.source_fps, frame

    def __len__(self) -> int:
        raise TypeError("frame count is unknown for this source")


def test_unknown_length_source_len_raises():
    source = UnknownLengthFrameSource(_make_frames(30), source_fps=30.0)
    with pytest.raises(TypeError):
        len(source)


def test_pipeline_unknown_length_source_not_empty(tmp_path):
    """전체 프레임 수를 모르는 소스도 프레임을 yield하면 매니페스트가 비지 않는다.

    Bug 2: 옛 run_capture는 len(source)==0을 믿어 빈 매니페스트를 만들었다.
    스트리밍 run_capture는 len을 호출하지 않고 프레임을 받아 샘플링한다.
    """
    source = UnknownLengthFrameSource(_make_frames(30), source_fps=30.0)
    manifest = run_capture(
        source=source,
        metadata=_metadata(),
        target_fps=10.0,
        output_dir=tmp_path / "frames",
        manifest_path=tmp_path / "manifest.json",
    )
    # 30fps -> 10fps, 1초(30프레임) -> 약 10프레임 (±1).
    assert len(manifest["frames"]) > 0, "프레임을 yield했는데 매니페스트가 비었다"
    assert abs(len(manifest["frames"]) - 10) <= 1
    # 저장된 파일도 실제로 존재.
    for record in manifest["frames"]:
        assert (tmp_path / record["image_path"]).exists()


def test_pipeline_unknown_length_source_genuinely_empty(tmp_path):
    """프레임을 0개 yield하는 unknown-length 소스는 빈 매니페스트가 정상."""
    source = UnknownLengthFrameSource([], source_fps=30.0)
    manifest = run_capture(
        source=source,
        metadata=_metadata(),
        target_fps=10.0,
        output_dir=tmp_path / "frames",
        manifest_path=tmp_path / "manifest.json",
    )
    assert manifest["frames"] == []
