import json
from pathlib import Path

import numpy as np

from object3d.adapters.segmentation.manual import (
    ManualBoxPredictor,
    load_prompt_json,
)
from object3d.adapters.segmentation.sam import SamPrompt, predict_mask
from object3d.capture.records import FrameRecord


def test_load_prompt_json_converts_box_and_points_to_sam_prompt(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.json"
    prompt_path.write_text(
        json.dumps(
            {
                "box_xyxy": [1, 2, 7, 5],
                "point_coords_xy": [[4, 3]],
                "point_labels": [1],
                "multimask_output": False,
            }
        ),
        encoding="utf-8",
    )

    prompt = load_prompt_json(prompt_path)

    assert prompt.box_xyxy == (1.0, 2.0, 7.0, 5.0)
    assert prompt.point_coords_xy == ((4.0, 3.0),)
    assert prompt.point_labels == (1,)
    assert prompt.multimask_output is False


def test_manual_box_predictor_produces_box_mask_through_sam_adapter() -> None:
    frame = FrameRecord(frame_id=0, image_path="frame.png", timestamp_s=0.0)
    image = np.zeros((6, 8, 3), dtype=np.uint8)

    mask = predict_mask(
        frame,
        image=image,
        object_id="object_001",
        predictor=ManualBoxPredictor(),
        prompt=SamPrompt(box_xyxy=(1.0, 2.0, 7.0, 5.0)),
    )

    assert mask.object_id == "object_001"
    assert mask.mask.shape == (6, 8)
    assert mask.mask.sum() == 18
    assert mask.mask[2:5, 1:7].all()
    assert mask.confidence == 1.0
