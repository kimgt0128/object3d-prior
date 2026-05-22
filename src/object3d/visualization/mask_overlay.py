"""2D mask overlay export."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from numpy.typing import NDArray


def export_mask_overlay(
    image: NDArray[np.uint8],
    mask: NDArray[np.bool_],
    output_path: Path,
    *,
    color_bgr: Tuple[int, int, int] = (0, 255, 0),
    alpha: float = 0.45,
) -> None:
    """이미지 위에 mask를 반투명 색으로 덧씌운 PNG를 저장한다."""
    if image.ndim != 3:
        raise ValueError("image must have shape (H, W, C)")
    if mask.shape != image.shape[:2]:
        raise ValueError("mask shape must match image height and width")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be between 0 and 1")

    output = image.copy()
    color_layer = np.zeros_like(image)
    color_layer[:, :] = np.array(color_bgr, dtype=np.uint8)
    blended = cv2.addWeighted(image, 1.0 - alpha, color_layer, alpha, 0.0)
    output[mask] = blended[mask]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), output):
        raise ValueError(f"failed to write overlay image: {output_path}")
