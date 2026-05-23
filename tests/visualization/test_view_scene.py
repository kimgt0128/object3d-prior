import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from object3d.contracts import ObjectPrior, PointCloudRecord
from object3d.visualization.export import export_scene_artifacts
from object3d.visualization.view_scene import (
    OptionalViewerDependencyError,
    load_scene_summary,
    main,
    read_ascii_ply,
    view_scene,
)


def _write_scene(tmp_path: Path) -> Path:
    cloud = PointCloudRecord(
        "object_001",
        np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32),
        (0, 1),
    )
    prior = ObjectPrior(
        object_id="object_001",
        center_xyz=np.array([0.5, 0.5, 0.5], dtype=np.float32),
        axes=np.eye(3, dtype=np.float32),
        dimensions_m=np.array([1.0, 1.0, 1.0], dtype=np.float32),
        confidence=1.0,
    )
    manifest = export_scene_artifacts(cloud, prior, tmp_path)
    return Path(manifest["assets"]["scene_manifest_json"])


def test_load_scene_summary_reports_assets(tmp_path: Path) -> None:
    manifest_path = _write_scene(tmp_path)

    summary = load_scene_summary(manifest_path)

    assert summary["object_id"] == "object_001"
    assert summary["bbox_type"] == "oriented"
    assert summary["asset_exists"] == {
        "point_cloud_ply": True,
        "bbox_ply": True,
        "scene_manifest_json": True,
    }


def test_read_ascii_ply_reads_vertices_and_edges(tmp_path: Path) -> None:
    manifest_path = _write_scene(tmp_path)
    summary = load_scene_summary(manifest_path)

    cloud = read_ascii_ply(Path(summary["assets"]["point_cloud_ply"]))
    bbox = read_ascii_ply(Path(summary["assets"]["bbox_ply"]))

    assert cloud.vertices.shape == (2, 3)
    assert cloud.edges == []
    assert bbox.vertices.shape == (8, 3)
    assert len(bbox.edges) == 12


def test_view_scene_summary_backend_returns_summary(tmp_path: Path) -> None:
    manifest_path = _write_scene(tmp_path)

    summary = view_scene(manifest_path, backend="summary")

    assert summary["backend"] == "summary"
    assert summary["object_id"] == "object_001"


def test_view_scene_rerun_backend_uses_lazy_dependency(
    monkeypatch,
    tmp_path: Path,
) -> None:
    manifest_path = _write_scene(tmp_path)
    seen: dict[str, object] = {"logs": []}
    rerun_module = types.ModuleType("rerun")

    def init(app_id: str, spawn: bool = False) -> None:
        seen["app_id"] = app_id
        seen["spawn"] = spawn

    def log(path: str, item) -> None:
        seen["logs"].append((path, item.__class__.__name__))

    class Points3D:
        def __init__(self, points) -> None:
            self.points = points

    class LineStrips3D:
        def __init__(self, strips) -> None:
            self.strips = strips

    rerun_module.init = init
    rerun_module.log = log
    rerun_module.Points3D = Points3D
    rerun_module.LineStrips3D = LineStrips3D
    monkeypatch.setitem(sys.modules, "rerun", rerun_module)

    summary = view_scene(
        manifest_path,
        backend="rerun",
        app_id="object3d-test",
        spawn=True,
    )

    assert summary["backend"] == "rerun"
    assert seen["app_id"] == "object3d-test"
    assert seen["spawn"] is True
    assert ("object_001/points", "Points3D") in seen["logs"]
    assert ("object_001/bbox", "LineStrips3D") in seen["logs"]


def test_view_scene_rerun_backend_can_save_recording(
    monkeypatch,
    tmp_path: Path,
) -> None:
    manifest_path = _write_scene(tmp_path)
    recording_path = tmp_path / "scene.rrd"
    seen: dict[str, object] = {"logs": []}
    rerun_module = types.ModuleType("rerun")

    def init(app_id: str, spawn: bool = False) -> None:
        seen["app_id"] = app_id
        seen["spawn"] = spawn

    def save(path: str) -> None:
        seen["save"] = path

    def log(path: str, item) -> None:
        seen["logs"].append((path, item.__class__.__name__))

    class Points3D:
        def __init__(self, points) -> None:
            self.points = points

    class LineStrips3D:
        def __init__(self, strips) -> None:
            self.strips = strips

    rerun_module.init = init
    rerun_module.save = save
    rerun_module.log = log
    rerun_module.Points3D = Points3D
    rerun_module.LineStrips3D = LineStrips3D
    monkeypatch.setitem(sys.modules, "rerun", rerun_module)

    summary = view_scene(
        manifest_path,
        backend="rerun",
        save_rrd=recording_path,
    )

    assert summary["backend"] == "rerun"
    assert summary["rerun_rrd"] == str(recording_path)
    assert seen["save"] == str(recording_path)


def test_view_scene_rerun_backend_reports_missing_dependency(
    monkeypatch,
    tmp_path: Path,
) -> None:
    manifest_path = _write_scene(tmp_path)
    monkeypatch.setitem(sys.modules, "rerun", None)

    with pytest.raises(OptionalViewerDependencyError, match="rerun"):
        view_scene(manifest_path, backend="rerun")


def test_view_scene_cli_prints_summary(
    capsys,
    tmp_path: Path,
) -> None:
    manifest_path = _write_scene(tmp_path)

    exit_code = main(
        [
            "--manifest",
            str(manifest_path),
            "--backend",
            "summary",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["backend"] == "summary"
    assert stdout["object_id"] == "object_001"


def test_view_scene_cli_accepts_save_rrd(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    manifest_path = _write_scene(tmp_path)
    recording_path = tmp_path / "scene.rrd"
    rerun_module = types.ModuleType("rerun")
    rerun_module.init = lambda app_id, spawn=False: None
    rerun_module.save = lambda path: None
    rerun_module.log = lambda path, item: None
    rerun_module.Points3D = lambda points: points
    rerun_module.LineStrips3D = lambda strips: strips
    monkeypatch.setitem(sys.modules, "rerun", rerun_module)

    exit_code = main(
        [
            "--manifest",
            str(manifest_path),
            "--backend",
            "rerun",
            "--save-rrd",
            str(recording_path),
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["backend"] == "rerun"
    assert stdout["rerun_rrd"] == str(recording_path)
