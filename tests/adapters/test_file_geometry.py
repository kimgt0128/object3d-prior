from pathlib import Path

import numpy as np
import pytest

from object3d.adapters.geometry.file import load_geometry_npz
from object3d.capture.records import FrameRecord
from object3d.geometry.backprojection import backproject_masked_points
from object3d.contracts import MaskRecord


def test_load_geometry_npz_returns_geometry_record_with_meter_depth(
    tmp_path: Path,
) -> None:
    path = tmp_path / "geometry.npz"
    depth = np.full((2, 3), 1.5, dtype=np.float32)
    intrinsics = np.array(
        [[100.0, 0.0, 1.0], [0.0, 100.0, 1.0], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    camera_to_world[:3, 3] = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    np.savez(
        path,
        depth_m=depth,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )
    frame = FrameRecord(frame_id=7, image_path="frame.png", timestamp_s=0.0)

    geometry = load_geometry_npz(path, frame)

    assert geometry.frame_id == 7
    assert geometry.depth_m.dtype == np.float32
    assert geometry.depth_m.shape == (2, 3)
    np.testing.assert_allclose(geometry.depth_m, depth)
    np.testing.assert_allclose(geometry.intrinsics, intrinsics)
    np.testing.assert_allclose(geometry.camera_to_world, camera_to_world)


def test_load_geometry_npz_output_works_with_backprojection(tmp_path: Path) -> None:
    path = tmp_path / "geometry.npz"
    np.savez(
        path,
        depth_m=np.ones((1, 1), dtype=np.float32) * 2.0,
        intrinsics=np.eye(3, dtype=np.float32),
        camera_to_world=np.eye(4, dtype=np.float32),
    )
    frame = FrameRecord(frame_id=0, image_path="frame.png", timestamp_s=0.0)
    geometry = load_geometry_npz(path, frame)
    mask = MaskRecord(0, "object_001", np.ones((1, 1), dtype=bool), 1.0)

    cloud = backproject_masked_points(mask, geometry)

    np.testing.assert_allclose(
        cloud.points_xyz,
        np.array([[0.0, 0.0, 2.0]], dtype=np.float32),
    )


def test_load_geometry_npz_rejects_world_to_camera_key(tmp_path: Path) -> None:
    path = tmp_path / "geometry.npz"
    np.savez(
        path,
        depth_m=np.ones((2, 2), dtype=np.float32),
        intrinsics=np.eye(3, dtype=np.float32),
        world_to_camera=np.eye(4, dtype=np.float32),
    )
    frame = FrameRecord(frame_id=0, image_path="frame.png", timestamp_s=0.0)

    with pytest.raises(ValueError, match="camera_to_world"):
        load_geometry_npz(path, frame)
