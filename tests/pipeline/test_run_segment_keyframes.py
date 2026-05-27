import json
from pathlib import Path

import cv2
import numpy as np

from object3d.capture.manifest import write_manifest
from object3d.capture.records import CaptureMetadata, FrameRecord
from object3d.pipeline import segment_keyframes
from object3d.pipeline.run_segment_keyframes import run_segment_keyframes


def _write_frame_manifest(tmp_path: Path, count: int = 2) -> Path:
    frames = []
    for frame_id in range(count):
        image_path = tmp_path / "keyframes" / f"frame_{frame_id:06d}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image = np.full((12, 16, 3), fill_value=frame_id * 20, dtype=np.uint8)
        cv2.imwrite(str(image_path), image)
        frames.append(
            FrameRecord(
                frame_id=frame_id,
                image_path=str(image_path.relative_to(tmp_path)),
                timestamp_s=float(frame_id * 2),
                camera_metadata={"source_index": frame_id * 60},
            )
        )

    manifest_path = tmp_path / "frame_manifest.json"
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


def _write_prompt_manifest(tmp_path: Path) -> Path:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_paths = []
    for frame_id in (0, 1):
        prompt_path = prompt_dir / f"laptop_frame_{frame_id:06d}.json"
        prompt_path.write_text(
            json.dumps({"box_xyxy": [2, 3, 10, 9]}) + "\n",
            encoding="utf-8",
        )
        prompt_paths.append(prompt_path)

    prompt_manifest_path = tmp_path / "object_prompts.json"
    prompt_manifest_path.write_text(
        json.dumps(
            {
                "objects": [
                    {
                        "object_id": "laptop_001",
                        "frames": [
                            {
                                "frame_id": frame_id,
                                "prompt_json": str(path.relative_to(tmp_path)),
                            }
                            for frame_id, path in enumerate(prompt_paths)
                        ],
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return prompt_manifest_path


def test_run_segment_keyframes_runs_manual_prompts_for_each_object_frame(
    tmp_path: Path,
) -> None:
    frame_manifest_path = _write_frame_manifest(tmp_path)
    prompt_manifest_path = _write_prompt_manifest(tmp_path)

    summary = run_segment_keyframes(
        frame_manifest_path=frame_manifest_path,
        prompt_manifest_path=prompt_manifest_path,
        output_dir=tmp_path / "segmentation",
        backend="manual",
    )

    assert summary["source"] == "segment_keyframes"
    assert summary["object_count"] == 1
    assert summary["segmentation_count"] == 2
    assert summary["objects"][0]["object_id"] == "laptop_001"
    assert [frame["frame_id"] for frame in summary["objects"][0]["frames"]] == [0, 1]
    assert Path(summary["summary_json"]).exists()

    for frame_summary in summary["objects"][0]["frames"]:
        assert Path(frame_summary["summary_json"]).exists()
        assert Path(frame_summary["mask_npy"]).exists()
        assert Path(frame_summary["overlay_png"]).exists()
        assert frame_summary["mask_pixels"] == 48

    saved_summary = json.loads(Path(summary["summary_json"]).read_text(encoding="utf-8"))
    assert saved_summary == summary


def test_segment_keyframes_cli_outputs_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    frame_manifest_path = tmp_path / "frame_manifest.json"
    prompt_manifest_path = tmp_path / "object_prompts.json"
    output_dir = tmp_path / "segmentation"
    checkpoint_path = tmp_path / "sam2.pt"
    config_path = tmp_path / "sam2.yaml"

    def fake_run_segment_keyframes(**kwargs):
        assert kwargs["frame_manifest_path"] == frame_manifest_path
        assert kwargs["prompt_manifest_path"] == prompt_manifest_path
        assert kwargs["output_dir"] == output_dir
        assert kwargs["backend"] == "sam2"
        assert kwargs["checkpoint_path"] == checkpoint_path
        assert kwargs["config_path"] == config_path
        assert kwargs["device"] == "cpu"
        return {
            "source": "segment_keyframes",
            "segmentation_count": 2,
        }

    monkeypatch.setattr(
        segment_keyframes,
        "run_segment_keyframes",
        fake_run_segment_keyframes,
    )

    exit_code = segment_keyframes.main(
        [
            "--frame-manifest",
            str(frame_manifest_path),
            "--prompt-manifest",
            str(prompt_manifest_path),
            "--output-dir",
            str(output_dir),
            "--backend",
            "sam2",
            "--checkpoint-path",
            str(checkpoint_path),
            "--config-path",
            str(config_path),
            "--device",
            "cpu",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["source"] == "segment_keyframes"
    assert stdout["segmentation_count"] == 2
