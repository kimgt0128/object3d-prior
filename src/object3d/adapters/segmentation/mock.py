"""SAM/SAM2 연동 전 downstream 검증용 mock segmentation adapter."""

from __future__ import annotations

from typing import Tuple

import numpy as np

from object3d.capture.records import FrameRecord
from object3d.contracts import MaskRecord


def make_center_box_mask(
    frame: FrameRecord,
    *,
    image_shape: Tuple[int, int],
    object_id: str,
    box_fraction: float,
) -> MaskRecord:
    """이미지 중앙 사각형을 객체 mask로 만든다."""
    if not 0.0 < box_fraction <= 1.0:
        raise ValueError("box_fraction must be in (0, 1]")

    height, width = image_shape
    mask = np.zeros((height, width), dtype=bool)
    box_width = int(width * box_fraction)
    box_height = int(height * box_fraction)
    x0 = (width - box_width) // 2
    y0 = (height - box_height) // 2
    mask[y0 : y0 + box_height, x0 : x0 + box_width] = True

    return MaskRecord(
        frame_id=frame.frame_id,
        object_id=object_id,
        mask=mask,
        confidence=1.0,
    )
