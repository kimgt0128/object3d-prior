import json
from pathlib import Path

import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.pipeline import fuse_object_priors
from object3d.pipeline.run_fuse_object_priors import run_fuse_object_priors
from object3d.visualization.export import export_point_cloud_ply


def _box_points(offset_x: float) -> np.ndarray:
    return np.array(
        [
            [0.0 + offset_x, 0.0, 1.0],
            [0.2 + offset_x, 0.0, 1.0],
            [0.0 + offset_x, 0.1, 1.0],
            [0.2 + offset_x, 0.1, 1.0],
            [0.0 + offset_x, 0.0, 1.1],
            [0.2 + offset_x, 0.0, 1.1],
            [0.0 + offset_x, 0.1, 1.1],
            [0.2 + offset_x, 0.1, 1.1],
        ],
        dtype=np.float32,
    )


def _write_prior_summary_with_cloud(
    tmp_path: Path,
    *,
    frame_id: int,
    offset_x: float,
    object_id: str = "object_001",
    include_outlier: bool = False,
) -> Path:
    prior_dir = tmp_path / f"prior_frame_{frame_id:06d}"
    prior_dir.mkdir(parents=True, exist_ok=True)
    cloud_path = prior_dir / f"{object_id}_cloud.ply"
    points = _box_points(offset_x)
    if include_outlier:
        points = np.concatenate(
            [points, np.array([[10.0, 10.0, 10.0]], dtype=np.float32)],
            axis=0,
        )
    cloud = PointCloudRecord(
        object_id=object_id,
        points_xyz=points,
        source_frame_ids=(frame_id,),
    )
    export_point_cloud_ply(cloud, cloud_path)
    summary_path = prior_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "source": "segmentation_summary",
                "object_id": object_id,
                "frame_id": frame_id,
                "point_count": int(len(cloud.points_xyz)),
                "point_cloud_ply": cloud_path.name,
                "summary_json": str(summary_path),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary_path


def test_run_fuse_object_priors_merges_same_object_clouds(tmp_path: Path) -> None:
    summary_paths = [
        _write_prior_summary_with_cloud(tmp_path, frame_id=0, offset_x=0.0),
        _write_prior_summary_with_cloud(tmp_path, frame_id=1, offset_x=0.1),
    ]

    summary = run_fuse_object_priors(
        prior_summary_paths=summary_paths,
        output_dir=tmp_path / "fused",
        outlier_filter="none",
    )

    assert summary["source"] == "fuse_object_priors"
    assert summary["object_id"] == "object_001"
    assert summary["input_prior_count"] == 2
    assert summary["source_frame_ids"] == [0, 1]
    assert summary["input_point_count"] == 16
    assert summary["filtered_point_count"] == 16
    assert summary["removed_point_count"] == 0
    assert len(summary["dimensions_m"]) == 3
    assert Path(summary["point_cloud_ply"]).exists()
    assert Path(summary["bbox_ply"]).exists()
    assert Path(summary["scene_manifest_json"]).exists()
    assert Path(summary["summary_json"]).exists()

    saved_summary = json.loads(Path(summary["summary_json"]).read_text(encoding="utf-8"))
    assert saved_summary == summary


def test_run_fuse_object_priors_can_filter_radial_outliers(tmp_path: Path) -> None:
    summary_path = _write_prior_summary_with_cloud(
        tmp_path,
        frame_id=0,
        offset_x=0.0,
        include_outlier=True,
    )

    summary = run_fuse_object_priors(
        prior_summary_paths=[summary_path],
        output_dir=tmp_path / "fused",
        outlier_filter="radial_percentile",
        outlier_keep_ratio=0.8,
    )

    assert summary["outlier_filter"] == "radial_percentile"
    assert summary["outlier_keep_ratio"] == 0.8
    assert summary["input_point_count"] == 9
    assert summary["filtered_point_count"] < summary["input_point_count"]
    assert summary["removed_point_count"] > 0


def test_fuse_object_priors_cli_outputs_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    prior_summary = tmp_path / "summary.json"
    output_dir = tmp_path / "fused"

    def fake_run_fuse_object_priors(**kwargs):
        assert kwargs["prior_summary_paths"] == [prior_summary]
        assert kwargs["output_dir"] == output_dir
        assert kwargs["outlier_filter"] == "radial_percentile"
        assert kwargs["outlier_keep_ratio"] == 0.9
        return {
            "source": "fuse_object_priors",
            "object_id": "object_001",
        }

    monkeypatch.setattr(
        fuse_object_priors,
        "run_fuse_object_priors",
        fake_run_fuse_object_priors,
    )

    exit_code = fuse_object_priors.main(
        [
            "--prior-summary",
            str(prior_summary),
            "--output-dir",
            str(output_dir),
            "--outlier-filter",
            "radial_percentile",
            "--outlier-keep-ratio",
            "0.9",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["source"] == "fuse_object_priors"
    assert stdout["object_id"] == "object_001"
