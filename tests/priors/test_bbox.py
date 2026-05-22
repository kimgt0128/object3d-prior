import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.priors.bbox import fit_axis_aligned_bbox


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
