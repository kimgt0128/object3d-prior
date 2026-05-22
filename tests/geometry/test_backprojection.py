import numpy as np

from object3d.contracts import GeometryRecord, MaskRecord
from object3d.geometry.backprojection import backproject_masked_points


def test_backproject_masked_points_uses_intrinsics_and_depth() -> None:
    depth = np.ones((3, 3), dtype=np.float32) * 2.0
    intrinsics = np.array(
        [[2.0, 0.0, 1.0], [0.0, 2.0, 1.0], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    geometry = GeometryRecord(0, depth, intrinsics, camera_to_world)
    mask_array = np.zeros((3, 3), dtype=bool)
    mask_array[1, 1] = True
    mask = MaskRecord(0, "object_001", mask_array, 1.0)

    cloud = backproject_masked_points(mask, geometry)

    assert cloud.object_id == "object_001"
    assert cloud.source_frame_ids == (0,)
    np.testing.assert_allclose(
        cloud.points_xyz,
        np.array([[0.0, 0.0, 2.0]], dtype=np.float32),
    )


def test_backproject_masked_points_applies_camera_to_world_translation() -> None:
    depth = np.ones((1, 1), dtype=np.float32)
    intrinsics = np.eye(3, dtype=np.float32)
    camera_to_world = np.eye(4, dtype=np.float32)
    camera_to_world[:3, 3] = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    geometry = GeometryRecord(0, depth, intrinsics, camera_to_world)
    mask = MaskRecord(0, "object_001", np.ones((1, 1), dtype=bool), 1.0)

    cloud = backproject_masked_points(mask, geometry)

    np.testing.assert_allclose(
        cloud.points_xyz,
        np.array([[10.0, 20.0, 31.0]], dtype=np.float32),
    )
