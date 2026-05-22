import json
from pathlib import Path

import cv2
import numpy as np

from object3d.pipeline.run_manual_segmentation import run_manual_segmentation
from object3d.pipeline.segment_image import main


def test_run_manual_segmentation_writes_mask_summary_and_overlay(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.png"
    prompt_path = tmp_path / "prompt.json"
    output_dir = tmp_path / "out"
    cv2.imwrite(str(image_path), np.zeros((10, 12, 3), dtype=np.uint8))
    prompt_path.write_text(json.dumps({"box_xyxy": [2, 3, 8, 7]}), encoding="utf-8")

    summary = run_manual_segmentation(
        image_path=image_path,
        prompt_json_path=prompt_path,
        output_dir=output_dir,
        object_id="object_001",
        frame_id=0,
    )

    assert Path(summary["mask_npy"]).exists()
    assert Path(summary["overlay_png"]).exists()
    assert Path(summary["summary_json"]).exists()
    assert summary["mask_pixels"] == 24
    saved_summary = json.loads(Path(summary["summary_json"]).read_text(encoding="utf-8"))
    assert saved_summary == summary
    assert np.load(summary["mask_npy"]).dtype == np.bool_


def test_segment_image_cli_runs_manual_segmentation(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "frame.png"
    prompt_path = tmp_path / "prompt.json"
    output_dir = tmp_path / "out"
    cv2.imwrite(str(image_path), np.zeros((10, 12, 3), dtype=np.uint8))
    prompt_path.write_text(json.dumps({"box_xyxy": [2, 3, 8, 7]}), encoding="utf-8")

    exit_code = main(
        [
            "--image-path",
            str(image_path),
            "--prompt-json",
            str(prompt_path),
            "--output-dir",
            str(output_dir),
            "--object-id",
            "object_001",
        ]
    )

    assert exit_code == 0
    stdout = json.loads(capsys.readouterr().out)
    assert stdout["object_id"] == "object_001"
    assert Path(stdout["overlay_png"]).exists()
