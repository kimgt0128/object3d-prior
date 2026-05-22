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
from object3d.adapters.segmentation.sam import load_sam_predictor, predict_mask
from object3d.capture.records import FrameRecord
from object3d.visualization.mask_overlay import export_mask_overlay


def run_manual_segmentation(
    *,
    image_path: Path,
    prompt_json_path: Path,
    output_dir: Path,
    object_id: str,
    frame_id: int,
    backend: str = "manual",
    checkpoint_path: Path | None = None,
    config_path: Path | None = None,
    device: str = "cpu",
    predictor_loader=None,
) -> dict[str, Any]:
    """prompt를 사용해 mask, overlay, summary를 저장한다."""
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
    if predictor_loader is None:
        predictor_loader = load_sam_predictor
    predictor = _build_predictor(
        backend=backend,
        checkpoint_path=checkpoint_path,
        config_path=config_path,
        device=device,
        predictor_loader=predictor_loader,
    )
    mask = predict_mask(
        frame,
        image=image,
        object_id=object_id,
        predictor=predictor,
        prompt=prompt,
    )

    mask_path = output_dir / "mask.npy"
    overlay_path = output_dir / "overlay.png"
    summary_path = output_dir / "summary.json"
    np.save(mask_path, mask.mask)
    export_mask_overlay(image, mask.mask, overlay_path)

    summary = {
        "backend": backend,
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


def _build_predictor(
    *,
    backend: str,
    checkpoint_path: Path | None,
    config_path: Path | None,
    device: str,
    predictor_loader,
):
    if backend == "manual":
        return ManualBoxPredictor()
    if backend == "sam2":
        if checkpoint_path is None:
            raise ValueError("checkpoint_path is required for backend='sam2'")
        if config_path is None:
            raise ValueError("config_path is required for backend='sam2'")
        return predictor_loader(
            backend="sam2",
            checkpoint_path=checkpoint_path,
            config_path=config_path,
            device=device,
        )
    raise ValueError("backend must be 'manual' or 'sam2'")
