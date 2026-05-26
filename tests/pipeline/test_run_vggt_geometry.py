import builtins
import json
from pathlib import Path

import numpy as np
import pytest

from object3d.adapters.geometry.file import load_geometry_npz
from object3d.adapters.geometry.vggt import OptionalGeometryDependencyError
from object3d.capture.records import FrameRecord
from object3d.pipeline import vggt_geometry
from object3d.pipeline.run_vggt_geometry import run_vggt_geometry


def test_run_vggt_geometry_writes_contract_with_injected_runner(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.png"
    image_path.write_bytes(b"fake image bytes")
    output_path = tmp_path / "geometry.npz"

    def fake_runner(*, image_paths, device, model_id):
        assert image_paths == (image_path,)
        assert device == "cuda"
        assert model_id == "fake/vggt"
        return {
            "depth_map": np.full((1, 3, 4, 1), 2.5, dtype=np.float32),
            "intrinsic": np.array(
                [
                    [
                        [100.0, 0.0, 2.0],
                        [0.0, 100.0, 1.5],
                        [0.0, 0.0, 1.0],
                    ]
                ],
                dtype=np.float32,
            ),
            "extrinsic": np.eye(4, dtype=np.float32)[None, ...],
        }

    summary = run_vggt_geometry(
        image_paths=[image_path],
        output_path=output_path,
        frame_index=0,
        device="cuda",
        model_id="fake/vggt",
        runner=fake_runner,
    )
    geometry = load_geometry_npz(
        output_path,
        FrameRecord(frame_id=0, image_path=str(image_path), timestamp_s=0.0),
    )

    assert summary["source"] == "vggt_geometry"
    assert summary["image_paths"] == [str(image_path)]
    assert summary["image_count"] == 1
    assert summary["device"] == "cuda"
    assert summary["model_id"] == "fake/vggt"
    assert summary["geometry_source"] == "vggt"
    assert summary["geometry_npz"] == str(output_path)
    assert Path(summary["summary_json"]).exists()
    np.testing.assert_allclose(geometry.depth_m, np.full((3, 4), 2.5, dtype=np.float32))

    saved_summary = json.loads(Path(summary["summary_json"]).read_text(encoding="utf-8"))
    assert saved_summary == summary


def test_run_vggt_geometry_rejects_empty_image_list(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least one"):
        run_vggt_geometry(
            image_paths=[],
            output_path=tmp_path / "geometry.npz",
            runner=lambda **_: {},
        )


def test_vggt_geometry_cli_prints_summary_from_runner(monkeypatch, tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "frame.png"
    image_path.write_bytes(b"fake image bytes")
    output_path = tmp_path / "geometry.npz"

    def fake_run_vggt_geometry(**kwargs):
        assert kwargs["image_paths"] == [image_path]
        assert kwargs["output_path"] == output_path
        assert kwargs["device"] == "mps"
        return {
            "source": "vggt_geometry",
            "geometry_npz": str(output_path),
            "image_count": 1,
        }

    monkeypatch.setattr(vggt_geometry, "run_vggt_geometry", fake_run_vggt_geometry)

    exit_code = vggt_geometry.main(
        [
            "--image-path",
            str(image_path),
            "--output-path",
            str(output_path),
            "--device",
            "mps",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["source"] == "vggt_geometry"
    assert stdout["geometry_npz"] == str(output_path)


def test_run_vggt_geometry_reports_optional_dependency_when_vggt_is_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("vggt"):
            raise ImportError("missing vggt")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    image_path = tmp_path / "frame.png"
    image_path.write_bytes(b"fake image bytes")

    with pytest.raises(OptionalGeometryDependencyError, match="vggt"):
        run_vggt_geometry(
            image_paths=[image_path],
            output_path=tmp_path / "geometry.npz",
        )
