import json
from pathlib import Path

import numpy as np

from object3d.adapters.geometry.file import load_geometry_npz
from object3d.capture.manifest import write_manifest
from object3d.capture.records import CaptureMetadata
from object3d.capture.records import FrameRecord
from object3d.pipeline import vggt_geometry_batch
from object3d.pipeline.run_vggt_geometry_batch import run_vggt_geometry_batch


def _write_manifest_with_images(tmp_path: Path, count: int = 3) -> Path:
    frames = []
    for frame_id in range(count):
        image_path = tmp_path / "frames" / f"frame_{frame_id:06d}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(b"fake image bytes")
        frames.append(
            FrameRecord(
                frame_id=frame_id,
                image_path=str(image_path.relative_to(tmp_path)),
                timestamp_s=float(frame_id),
                camera_metadata={"source_index": frame_id * 3},
            )
        )
    manifest_path = tmp_path / "manifest.json"
    write_manifest(
        {
            "schema_version": 1,
            "capture_metadata": CaptureMetadata(
                object_name="room",
                measured_cm={},
                camera_mode="handheld_video",
                lighting="indoor",
                material="mixed_room",
                source_video="synthetic://room",
                source_fps=30.0,
            ).to_dict(),
            "frames": [frame.to_dict() for frame in frames],
        },
        manifest_path,
    )
    return manifest_path


def test_run_vggt_geometry_batch_writes_one_geometry_per_frame(
    tmp_path: Path,
) -> None:
    manifest_path = _write_manifest_with_images(tmp_path, count=3)

    def fake_runner(*, image_paths, device, model_id):
        assert len(image_paths) == 3
        assert device == "cpu"
        assert model_id == "fake/vggt"
        return {
            "depth_map": np.stack(
                [
                    np.full((4, 5, 1), 1.0 + index, dtype=np.float32)
                    for index in range(3)
                ],
                axis=0,
            ),
            "intrinsic": np.repeat(np.eye(3, dtype=np.float32)[None], 3, axis=0),
            "extrinsic": np.repeat(np.eye(3, 4, dtype=np.float32)[None], 3, axis=0),
        }

    summary = run_vggt_geometry_batch(
        manifest_path=manifest_path,
        output_dir=tmp_path / "geometry",
        device="cpu",
        model_id="fake/vggt",
        runner=fake_runner,
    )

    assert summary["source"] == "vggt_geometry_batch"
    assert summary["frame_count"] == 3
    assert summary["geometry_count"] == 3
    assert [item["frame_id"] for item in summary["geometries"]] == [0, 1, 2]
    assert [item["frame_index"] for item in summary["geometries"]] == [0, 1, 2]
    assert [item["geometry_depth_shape"] for item in summary["geometries"]] == [
        [4, 5],
        [4, 5],
        [4, 5],
    ]
    assert Path(summary["summary_json"]).exists()

    for index, item in enumerate(summary["geometries"]):
        geometry_path = Path(item["geometry_npz"])
        assert geometry_path.exists()
        geometry = load_geometry_npz(
            geometry_path,
            FrameRecord(
                frame_id=item["frame_id"],
                image_path=item["image_path"],
                timestamp_s=item["timestamp_s"],
            ),
        )
        np.testing.assert_allclose(
            geometry.depth_m,
            np.full((4, 5), 1.0 + index, dtype=np.float32),
        )

    saved_summary = json.loads(Path(summary["summary_json"]).read_text(encoding="utf-8"))
    assert saved_summary == summary


def test_run_vggt_geometry_batch_respects_max_frames(tmp_path: Path) -> None:
    manifest_path = _write_manifest_with_images(tmp_path, count=4)

    def fake_runner(*, image_paths, device, model_id):
        assert len(image_paths) == 2
        return {
            "depth_map": np.ones((2, 2, 3, 1), dtype=np.float32),
            "intrinsic": np.repeat(np.eye(3, dtype=np.float32)[None], 2, axis=0),
            "extrinsic": np.repeat(np.eye(3, 4, dtype=np.float32)[None], 2, axis=0),
        }

    summary = run_vggt_geometry_batch(
        manifest_path=manifest_path,
        output_dir=tmp_path / "geometry",
        max_frames=2,
        runner=fake_runner,
    )

    assert summary["frame_count"] == 2
    assert summary["geometry_count"] == 2


def test_vggt_geometry_batch_cli_outputs_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "manifest.json"
    output_dir = tmp_path / "geometry"

    def fake_run_vggt_geometry_batch(**kwargs):
        assert kwargs["manifest_path"] == manifest_path
        assert kwargs["output_dir"] == output_dir
        assert kwargs["device"] == "mps"
        assert kwargs["model_id"] == "fake/vggt"
        assert kwargs["max_frames"] == 8
        return {
            "source": "vggt_geometry_batch",
            "geometry_count": 8,
        }

    monkeypatch.setattr(
        vggt_geometry_batch,
        "run_vggt_geometry_batch",
        fake_run_vggt_geometry_batch,
    )

    exit_code = vggt_geometry_batch.main(
        [
            "--manifest",
            str(manifest_path),
            "--output-dir",
            str(output_dir),
            "--device",
            "mps",
            "--model-id",
            "fake/vggt",
            "--max-frames",
            "8",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["source"] == "vggt_geometry_batch"
    assert stdout["geometry_count"] == 8
