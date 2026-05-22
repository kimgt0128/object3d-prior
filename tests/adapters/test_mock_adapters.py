import numpy as np

from object3d.adapters.geometry.mock import make_planar_mock_geometry
from object3d.adapters.segmentation.mock import make_center_box_mask
from object3d.capture.records import FrameRecord


def test_make_center_box_mask_returns_bool_mask() -> None:
    frame = FrameRecord(
        frame_id=0,
        image_path="frame_000000.png",
        timestamp_s=0.0,
    )

    mask = make_center_box_mask(
        frame,
        image_shape=(80, 100),
        object_id="object_001",
        box_fraction=0.5,
    )

    assert mask.frame_id == 0
    assert mask.object_id == "object_001"
    assert mask.mask.dtype == np.bool_
    assert mask.mask.shape == (80, 100)
    assert mask.mask.sum() == 40 * 50


def test_make_planar_mock_geometry_shapes() -> None:
    frame = FrameRecord(
        frame_id=0,
        image_path="frame_000000.png",
        timestamp_s=0.0,
    )

    geometry = make_planar_mock_geometry(
        frame,
        image_shape=(80, 100),
        depth_m=2.0,
    )

    assert geometry.frame_id == 0
    assert geometry.depth_m.shape == (80, 100)
    assert geometry.intrinsics.shape == (3, 3)
    assert geometry.camera_to_world.shape == (4, 4)
    assert float(geometry.depth_m[0, 0]) == 2.0
