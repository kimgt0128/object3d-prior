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


def fit_oriented_bbox(cloud: PointCloudRecord) -> ObjectPrior:
    """PCA 주축 좌표계에서 객체 중심과 크기를 추정한다."""
    if cloud.points_xyz.size == 0:
        raise ValueError("cannot fit bbox to an empty point cloud")

    points = cloud.points_xyz.astype(np.float32, copy=False)
    mean = points.mean(axis=0)
    centered = points - mean
    axes = _principal_axes(centered)
    local_points = centered @ axes
    mins = local_points.min(axis=0)
    maxs = local_points.max(axis=0)
    local_center = (mins + maxs) / 2.0
    center = mean + local_center @ axes.T
    dimensions = maxs - mins

    return ObjectPrior(
        object_id=cloud.object_id,
        center_xyz=center.astype(np.float32),
        axes=axes.astype(np.float32),
        dimensions_m=dimensions.astype(np.float32),
        confidence=1.0,
    )


def _principal_axes(centered_points: np.ndarray) -> np.ndarray:
    if centered_points.shape[0] < 2 or np.allclose(centered_points, 0.0):
        return np.eye(3, dtype=np.float32)

    covariance = np.cov(centered_points, rowvar=False, bias=True)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    axes = eigenvectors[:, order].astype(np.float32)

    if np.linalg.det(axes) < 0:
        axes[:, -1] *= -1.0
    return axes
