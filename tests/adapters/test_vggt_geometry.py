from pathlib import Path
import builtins

import numpy as np
import pytest

from object3d.adapters.geometry.file import load_geometry_npz
from object3d.adapters.geometry.vggt import (
    OptionalGeometryDependencyError,
    load_vggt_model,
    save_vggt_geometry_npz,
)
from object3d.capture.records import FrameRecord


def test_save_vggt_geometry_npz_converts_prediction_to_contract(tmp_path: Path) -> None:
    output_path = tmp_path / "geometry.npz"
    world_to_camera = np.eye(4, dtype=np.float32)
    world_to_camera[:3, 3] = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    prediction = {
        "depth_map": np.full((1, 2, 3), 2.5, dtype=np.float32),
        "intrinsic": np.array(
            [
                [
                    [100.0, 0.0, 1.5],
                    [0.0, 100.0, 1.0],
                    [0.0, 0.0, 1.0],
                ]
            ],
            dtype=np.float32,
        ),
        "extrinsic": world_to_camera[None, ...],
    }

    summary = save_vggt_geometry_npz(
        prediction,
        output_path=output_path,
        frame_index=0,
    )
    geometry = load_geometry_npz(
        output_path,
        FrameRecord(frame_id=11, image_path="frame.png", timestamp_s=0.0),
    )

    assert summary == {
        "geometry_npz": str(output_path),
        "geometry_source": "vggt",
        "frame_index": 0,
    }
    np.testing.assert_allclose(geometry.depth_m, np.full((2, 3), 2.5, dtype=np.float32))
    np.testing.assert_allclose(geometry.intrinsics, prediction["intrinsic"][0])
    np.testing.assert_allclose(
        geometry.camera_to_world,
        np.linalg.inv(world_to_camera),
    )


def test_save_vggt_geometry_npz_accepts_plural_prediction_keys(tmp_path: Path) -> None:
    output_path = tmp_path / "geometry.npz"
    prediction = {
        "depth_maps": np.ones((2, 4, 5, 1), dtype=np.float32),
        "intrinsics": np.repeat(np.eye(3, dtype=np.float32)[None, ...], 2, axis=0),
        "extrinsics": np.repeat(np.eye(4, dtype=np.float32)[None, ...], 2, axis=0),
    }

    save_vggt_geometry_npz(
        prediction,
        output_path=output_path,
        frame_index=1,
    )

    with np.load(output_path) as payload:
        assert payload["depth_m"].shape == (4, 5)
        assert payload["intrinsics"].shape == (3, 3)
        assert payload["camera_to_world"].shape == (4, 4)


def test_save_vggt_geometry_npz_rejects_missing_prediction_keys(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="depth"):
        save_vggt_geometry_npz(
            {"intrinsic": np.eye(3), "extrinsic": np.eye(4)},
            output_path=tmp_path / "geometry.npz",
        )


def test_load_vggt_model_reports_optional_dependency_when_missing(monkeypatch) -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("vggt"):
            raise ImportError("missing vggt")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(OptionalGeometryDependencyError, match="vggt"):
        load_vggt_model()
