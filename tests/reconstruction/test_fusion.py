import numpy as np
import pytest

from object3d.contracts import PointCloudRecord
from object3d.reconstruction.fusion import fuse_point_clouds


def test_fuse_point_clouds_concatenates_points_and_sources() -> None:
    first = PointCloudRecord(
        "object_001",
        np.array([[0.0, 0.0, 1.0]], dtype=np.float32),
        (0,),
    )
    second = PointCloudRecord(
        "object_001",
        np.array([[1.0, 0.0, 1.0]], dtype=np.float32),
        (1,),
    )

    fused = fuse_point_clouds([first, second])

    assert fused.object_id == "object_001"
    assert fused.points_xyz.shape == (2, 3)
    assert fused.source_frame_ids == (0, 1)


def test_fuse_point_clouds_rejects_mixed_object_ids() -> None:
    first = PointCloudRecord("a", np.zeros((1, 3), dtype=np.float32), (0,))
    second = PointCloudRecord("b", np.zeros((1, 3), dtype=np.float32), (1,))

    with pytest.raises(ValueError, match="same object_id"):
        fuse_point_clouds([first, second])
