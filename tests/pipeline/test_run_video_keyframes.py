import json
from pathlib import Path

import numpy as np
import pytest

from object3d.capture.frame_source import ArrayFrameSource
from object3d.capture.manifest import read_manifest
from object3d.pipeline import video_keyframes
from object3d.pipeline.run_video_keyframes import run_video_keyframes


def _make_frames(count: int) -> list[np.ndarray]:
    return [
        np.full((8, 8, 3), fill_value=index, dtype=np.uint8)
        for index in range(count)
    ]


def test_run_video_keyframes_writes_manifest_with_sampled_frames(
    tmp_path: Path,
) -> None:
    source = ArrayFrameSource(_make_frames(12), source_fps=6.0)

    summary = run_video_keyframes(
        source=source,
        source_video="synthetic://room",
        output_dir=tmp_path / "frames",
        manifest_path=tmp_path / "manifest.json",
        target_fps=2.0,
    )

    assert summary["source"] == "video_keyframes"
    assert summary["source_video"] == "synthetic://room"
    assert summary["source_fps"] == 6.0
    assert summary["target_fps"] == 2.0
    assert summary["frame_count"] == 4
    assert summary["frame_ids"] == [0, 1, 2, 3]
    assert summary["source_indices"] == [0, 3, 6, 9]
    assert Path(summary["manifest_json"]).exists()
    assert all(Path(path).exists() for path in summary["frame_paths"])

    manifest = read_manifest(tmp_path / "manifest.json")
    assert len(manifest["frames"]) == 4
    assert manifest["capture_metadata"]["source_video"] == "synthetic://room"


def test_run_video_keyframes_rejects_empty_frame_source(tmp_path: Path) -> None:
    source = ArrayFrameSource([], source_fps=30.0)

    with pytest.raises(ValueError, match="did not produce any keyframes"):
        run_video_keyframes(
            source=source,
            source_video="synthetic://empty-room",
            output_dir=tmp_path / "frames",
            manifest_path=tmp_path / "manifest.json",
            target_fps=0.5,
        )


def test_video_keyframes_cli_outputs_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    video_path = tmp_path / "room.mp4"
    output_dir = tmp_path / "frames"
    manifest_path = tmp_path / "manifest.json"

    def fake_run_video_keyframes(**kwargs):
        assert kwargs["source_video"] == str(video_path)
        assert kwargs["output_dir"] == output_dir
        assert kwargs["manifest_path"] == manifest_path
        assert kwargs["target_fps"] == 0.5
        return {
            "source": "video_keyframes",
            "frame_count": 8,
            "manifest_json": str(manifest_path),
        }

    class FakeVideoFrameSource:
        def __init__(self, path):
            assert path == str(video_path)
            self.source_fps = 30.0

        def iter_frames(self):
            return iter(())

        def __len__(self):
            return 0

    monkeypatch.setattr(video_keyframes, "VideoFrameSource", FakeVideoFrameSource)
    monkeypatch.setattr(
        video_keyframes,
        "run_video_keyframes",
        fake_run_video_keyframes,
    )

    exit_code = video_keyframes.main(
        [
            "--video-path",
            str(video_path),
            "--output-dir",
            str(output_dir),
            "--manifest-path",
            str(manifest_path),
            "--target-fps",
            "0.5",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["source"] == "video_keyframes"
    assert stdout["frame_count"] == 8
