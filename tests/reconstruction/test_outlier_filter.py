import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.reconstruction.outlier_filter import (
    filter_point_cloud_radial_percentile,
)


def test_filter_point_cloud_radial_percentile_removes_far_tail() -> None:
    cloud = PointCloudRecord(
        object_id="laptop_001",
        points_xyz=np.array(
            [
                [0.00, 0.00, 1.00],
                [0.01, 0.00, 1.01],
                [-0.01, 0.00, 0.99],
                [0.00, 0.01, 1.00],
                [0.00, -0.01, 1.00],
                [5.00, 5.00, 8.00],
            ],
            dtype=np.float32,
        ),
        source_frame_ids=(0,),
    )

    filtered, summary = filter_point_cloud_radial_percentile(
        cloud,
        keep_ratio=0.90,
    )

    assert filtered.object_id == "laptop_001"
    assert filtered.source_frame_ids == (0,)
    assert len(filtered.points_xyz) == 5
    assert summary == {
        "outlier_filter": "radial_percentile",
        "outlier_keep_ratio": 0.9,
        "input_point_count": 6,
        "filtered_point_count": 5,
        "removed_point_count": 1,
    }
    assert not np.any(np.all(filtered.points_xyz == [5.0, 5.0, 8.0], axis=1))


def test_filter_point_cloud_radial_percentile_rejects_invalid_keep_ratio() -> None:
    cloud = PointCloudRecord(
        object_id="object_001",
        points_xyz=np.zeros((3, 3), dtype=np.float32),
        source_frame_ids=(0,),
    )

    import pytest

    with pytest.raises(ValueError, match="keep_ratio"):
        filter_point_cloud_radial_percentile(cloud, keep_ratio=1.0)
