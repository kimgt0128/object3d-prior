"""프레임별 객체 point cloud를 객체 단위 cloud로 합친다."""

from __future__ import annotations

import numpy as np

from object3d.contracts import PointCloudRecord


def fuse_point_clouds(clouds: list[PointCloudRecord]) -> PointCloudRecord:
    """같은 객체의 여러 frame point cloud를 하나로 합친다."""
    if not clouds:
        raise ValueError("clouds must not be empty")

    object_id = clouds[0].object_id
    if any(cloud.object_id != object_id for cloud in clouds):
        raise ValueError("all clouds must have the same object_id")

    points = np.concatenate([cloud.points_xyz for cloud in clouds], axis=0).astype(
        np.float32
    )
    frame_ids: list[int] = []
    for cloud in clouds:
        frame_ids.extend(cloud.source_frame_ids)

    return PointCloudRecord(
        object_id=object_id,
        points_xyz=points,
        source_frame_ids=tuple(frame_ids),
    )
