"""downstream MVP 단계에서 공유하는 3D 데이터 계약."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class MaskRecord:
    """단일 프레임의 객체 mask."""

    frame_id: int
    object_id: str
    mask: BoolArray
    confidence: float

    def __post_init__(self) -> None:
        if self.mask.ndim != 2:
            raise ValueError("mask must be a 2D array")
        if self.mask.dtype != np.bool_:
            raise ValueError("mask dtype must be bool")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class GeometryRecord:
    """단일 프레임의 depth와 camera geometry."""

    frame_id: int
    depth_m: FloatArray
    intrinsics: FloatArray
    camera_to_world: FloatArray

    def __post_init__(self) -> None:
        if self.depth_m.ndim != 2:
            raise ValueError("depth_m must be a 2D array")
        if self.intrinsics.shape != (3, 3):
            raise ValueError("intrinsics must have shape (3, 3)")
        if self.camera_to_world.shape != (4, 4):
            raise ValueError("camera_to_world must have shape (4, 4)")


@dataclass(frozen=True)
class PointCloudRecord:
    """객체 단위 3D point cloud."""

    object_id: str
    points_xyz: FloatArray
    source_frame_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.points_xyz.ndim != 2 or self.points_xyz.shape[1] != 3:
            raise ValueError("points_xyz must have shape (N, 3)")


@dataclass(frozen=True)
class ObjectPrior:
    """후속 단계가 소비할 객체 3D prior."""

    object_id: str
    center_xyz: FloatArray
    axes: FloatArray
    dimensions_m: FloatArray
    confidence: float

    def __post_init__(self) -> None:
        if self.center_xyz.shape != (3,):
            raise ValueError("center_xyz must have shape (3,)")
        if self.axes.shape != (3, 3):
            raise ValueError("axes must have shape (3, 3)")
        if self.dimensions_m.shape != (3,):
            raise ValueError("dimensions_m must have shape (3,)")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
