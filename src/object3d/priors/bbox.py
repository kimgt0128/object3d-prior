"""Bounding box 기반 object prior fitting."""

from __future__ import annotations

import numpy as np

from object3d.contracts import ObjectPrior, PointCloudRecord


def fit_axis_aligned_bbox(cloud: PointCloudRecord) -> ObjectPrior:
    """axis-aligned bbox로 객체 중심과 크기를 추정한다."""
    if cloud.points_xyz.size == 0:
        raise ValueError("cannot fit bbox to an empty point cloud")

    mins = cloud.points_xyz.min(axis=0)
    maxs = cloud.points_xyz.max(axis=0)
    center = ((mins + maxs) / 2.0).astype(np.float32)
    dimensions = (maxs - mins).astype(np.float32)
    axes = np.eye(3, dtype=np.float32)

    return ObjectPrior(
        object_id=cloud.object_id,
        center_xyz=center,
        axes=axes,
        dimensions_m=dimensions,
        confidence=1.0,
    )
