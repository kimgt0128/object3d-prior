"""Point cloud outlier filtering utilities."""

from __future__ import annotations

from typing import Any

import numpy as np

from object3d.contracts import PointCloudRecord


def filter_point_cloud_radial_percentile(
    cloud: PointCloudRecord,
    *,
    keep_ratio: float,
) -> tuple[PointCloudRecord, dict[str, Any]]:
    """Remove the farthest radial tail around the median point."""
    if not 0.0 < keep_ratio < 1.0:
        raise ValueError("keep_ratio must be greater than 0 and less than 1")

    point_count = int(len(cloud.points_xyz))
    if point_count == 0:
        return cloud, _summary(
            keep_ratio=keep_ratio,
            input_count=0,
            filtered_count=0,
        )
    if point_count < 3:
        return cloud, _summary(
            keep_ratio=keep_ratio,
            input_count=point_count,
            filtered_count=point_count,
        )

    center = np.median(cloud.points_xyz, axis=0)
    distances = np.linalg.norm(cloud.points_xyz - center, axis=1)
    threshold = float(np.quantile(distances, keep_ratio))
    keep_mask = distances <= threshold
    if not np.any(keep_mask):
        keep_mask[np.argmin(distances)] = True

    filtered_points = np.asarray(cloud.points_xyz[keep_mask], dtype=np.float32)
    filtered = PointCloudRecord(
        object_id=cloud.object_id,
        points_xyz=filtered_points,
        source_frame_ids=cloud.source_frame_ids,
    )
    return filtered, _summary(
        keep_ratio=keep_ratio,
        input_count=point_count,
        filtered_count=int(len(filtered_points)),
    )


def _summary(
    *,
    keep_ratio: float,
    input_count: int,
    filtered_count: int,
) -> dict[str, Any]:
    return {
        "outlier_filter": "radial_percentile",
        "outlier_keep_ratio": float(keep_ratio),
        "input_point_count": int(input_count),
        "filtered_point_count": int(filtered_count),
        "removed_point_count": int(input_count - filtered_count),
    }
