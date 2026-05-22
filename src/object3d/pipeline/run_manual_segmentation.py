"""이미지와 수동 prompt JSON으로 segmentation 산출물을 만든다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from object3d.adapters.segmentation.manual import (
    ManualBoxPredictor,
    load_prompt_json,
)
from object3d.adapters.segmentation.sam import predict_mask
from object3d.capture.records import FrameRecord
from object3d.visualization.mask_overlay import export_mask_overlay


def run_manual_segmentation(
    *,
    image_path: Path,
    prompt_json_path: Path,
    output_dir: Path,
    object_id: str,
    frame_id: int,
) -> dict[str, Any]:
    """수동 prompt를 사용해 mask, overlay, summary를 저장한다."""
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"failed to read image: {image_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    frame = FrameRecord(
        frame_id=frame_id,
        image_path=str(image_path),
        timestamp_s=0.0,
    )
    prompt = load_prompt_json(prompt_json_path)
    mask = predict_mask(
        frame,
        image=image,
        object_id=object_id,
        predictor=ManualBoxPredictor(),
        prompt=prompt,
    )

    mask_path = output_dir / "mask.npy"
    overlay_path = output_dir / "overlay.png"
    summary_path = output_dir / "summary.json"
    np.save(mask_path, mask.mask)
    export_mask_overlay(image, mask.mask, overlay_path)

    summary = {
        "object_id": mask.object_id,
        "frame_id": mask.frame_id,
        "image_path": str(image_path),
        "prompt_json": str(prompt_json_path),
        "confidence": mask.confidence,
        "mask_shape": list(mask.mask.shape),
        "mask_pixels": int(mask.mask.sum()),
        "mask_npy": str(mask_path),
        "overlay_png": str(overlay_path),
        "summary_json": str(summary_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
