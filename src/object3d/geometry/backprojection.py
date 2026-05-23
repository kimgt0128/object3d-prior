"""Pinhole camera model 기반 masked back-projection."""

from __future__ import annotations

import numpy as np

from object3d.contracts import GeometryRecord, MaskRecord, PointCloudRecord


def backproject_masked_points(
    mask: MaskRecord,
    geometry: GeometryRecord,
) -> PointCloudRecord:
    """mask 영역의 pixel만 world-space 3D point로 역투영한다."""
    if mask.frame_id != geometry.frame_id:
        raise ValueError("mask and geometry must belong to the same frame")
    if mask.mask.shape != geometry.depth_m.shape:
        raise ValueError("mask and depth must have the same shape")

    v_coords, u_coords = np.nonzero(mask.mask)
    if len(u_coords) == 0:
        return PointCloudRecord(
            object_id=mask.object_id,
            points_xyz=np.empty((0, 3), dtype=np.float32),
            source_frame_ids=(mask.frame_id,),
        )

    depth = geometry.depth_m[v_coords, u_coords].astype(np.float32)
    fx = float(geometry.intrinsics[0, 0])
    fy = float(geometry.intrinsics[1, 1])
    cx = float(geometry.intrinsics[0, 2])
    cy = float(geometry.intrinsics[1, 2])

    if fx == 0 or fy == 0:
        raise ValueError("focal lengths must be non-zero")

    x = (u_coords.astype(np.float32) - cx) * depth / fx
    y = (v_coords.astype(np.float32) - cy) * depth / fy
    z = depth

    camera_points = np.stack([x, y, z], axis=1)
    rotation = geometry.camera_to_world[:3, :3]
    translation = geometry.camera_to_world[:3, 3]
    world_points = camera_points @ rotation.T + translation

    return PointCloudRecord(
        object_id=mask.object_id,
        points_xyz=world_points.astype(np.float32),
        source_frame_ids=(mask.frame_id,),
    )
