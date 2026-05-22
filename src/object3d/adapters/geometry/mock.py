"""실 geometry 모델 연동 전 downstream 검증용 mock geometry adapter."""

from __future__ import annotations

from typing import Tuple

import numpy as np

from object3d.capture.records import FrameRecord
from object3d.contracts import GeometryRecord


def make_planar_mock_geometry(
    frame: FrameRecord,
    *,
    image_shape: Tuple[int, int],
    depth_m: float,
) -> GeometryRecord:
    """전체 이미지가 일정 depth에 놓인 평면이라고 가정한다."""
    if depth_m <= 0:
        raise ValueError("depth_m must be positive")

    height, width = image_shape
    depth = np.full((height, width), depth_m, dtype=np.float32)
    focal = float(max(width, height))
    intrinsics = np.array(
        [
            [focal, 0.0, width / 2.0],
            [0.0, focal, height / 2.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    return GeometryRecord(
        frame_id=frame.frame_id,
        depth_m=depth,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )
