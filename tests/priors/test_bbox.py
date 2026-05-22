import numpy as np
import pytest

from object3d.contracts import PointCloudRecord
from object3d.priors.bbox import fit_axis_aligned_bbox, fit_oriented_bbox


def test_fit_axis_aligned_bbox_reports_dimensions() -> None:
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 3.0, 4.0],
            [1.0, 2.0, 3.0],
        ],
        dtype=np.float32,
    )
    cloud = PointCloudRecord("object_001", points, (0,))

    prior = fit_axis_aligned_bbox(cloud)

    np.testing.assert_allclose(
        prior.center_xyz,
        np.array([1.0, 1.5, 2.0], dtype=np.float32),
    )
    np.testing.assert_allclose(
        prior.dimensions_m,
        np.array([2.0, 3.0, 4.0], dtype=np.float32),
    )
    np.testing.assert_allclose(prior.axes, np.eye(3, dtype=np.float32))
    assert prior.confidence == 1.0


def test_fit_oriented_bbox_reports_dimensions_for_rotated_box() -> None:
    dimensions = np.array([4.0, 2.0, 1.0], dtype=np.float32)
    half = dimensions / 2.0
    corners = np.array(
        [
            [x, y, z]
            for x in (-half[0], half[0])
            for y in (-half[1], half[1])
            for z in (-half[2], half[2])
        ],
        dtype=np.float32,
    )
    theta = np.deg2rad(30.0)
    rotation = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0.0],
            [np.sin(theta), np.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    center = np.array([10.0, -2.0, 0.5], dtype=np.float32)
    points = corners @ rotation.T + center
    cloud = PointCloudRecord("object_001", points.astype(np.float32), (0, 1))

    prior = fit_oriented_bbox(cloud)

    np.testing.assert_allclose(prior.center_xyz, center, atol=1e-5)
    np.testing.assert_allclose(prior.dimensions_m, dimensions, atol=1e-5)
    np.testing.assert_allclose(prior.axes.T @ prior.axes, np.eye(3), atol=1e-5)
    assert abs(float(prior.axes[:, 0] @ rotation[:, 0])) == pytest.approx(1.0)
    assert np.linalg.det(prior.axes) == pytest.approx(1.0)
