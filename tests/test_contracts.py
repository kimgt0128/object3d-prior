import numpy as np
import pytest

from object3d.contracts import GeometryRecord, MaskRecord, ObjectPrior, PointCloudRecord


def test_mask_record_validates_mask_shape_and_dtype() -> None:
    mask = np.ones((4, 5), dtype=bool)

    record = MaskRecord(
        frame_id=0,
        object_id="object_001",
        mask=mask,
        confidence=0.95,
    )

    assert record.mask.dtype == np.bool_
    assert record.mask.shape == (4, 5)


def test_mask_record_rejects_non_bool_mask() -> None:
    with pytest.raises(ValueError, match="mask dtype"):
        MaskRecord(
            frame_id=0,
            object_id="object_001",
            mask=np.ones((4, 5), dtype=np.uint8),
            confidence=0.95,
        )


def test_geometry_record_contains_camera_matrices() -> None:
    depth = np.ones((2, 3), dtype=np.float32)
    intrinsics = np.eye(3, dtype=np.float32)
    camera_to_world = np.eye(4, dtype=np.float32)

    record = GeometryRecord(
        frame_id=0,
        depth_m=depth,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )

    assert record.depth_m.shape == (2, 3)
    assert record.intrinsics.shape == (3, 3)
    assert record.camera_to_world.shape == (4, 4)


def test_point_cloud_and_prior_contracts_keep_object_identity() -> None:
    points = np.array([[0.0, 0.0, 1.0]], dtype=np.float32)
    cloud = PointCloudRecord(
        object_id="object_001",
        points_xyz=points,
        source_frame_ids=(0,),
    )
    prior = ObjectPrior(
        object_id=cloud.object_id,
        center_xyz=np.array([0.0, 0.0, 1.0], dtype=np.float32),
        axes=np.eye(3, dtype=np.float32),
        dimensions_m=np.array([1.0, 1.0, 1.0], dtype=np.float32),
        confidence=1.0,
    )

    assert cloud.object_id == "object_001"
    assert prior.object_id == "object_001"
