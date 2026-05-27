"""Object-aware fusion helper for per-frame object prior summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.priors.bbox import fit_oriented_bbox
from object3d.reconstruction.fusion import fuse_point_clouds
from object3d.reconstruction.outlier_filter import (
    filter_point_cloud_radial_percentile,
)
from object3d.visualization.export import export_scene_artifacts
from object3d.visualization.view_scene import read_ascii_ply


def run_fuse_object_priors(
    *,
    prior_summary_paths: list[Path],
    output_dir: Path,
    outlier_filter: str = "none",
    outlier_keep_ratio: float = 0.95,
) -> dict[str, Any]:
    """Fuse per-frame object prior point clouds into one object prior."""
    if not prior_summary_paths:
        raise ValueError("prior_summary_paths must not be empty")

    clouds = [_load_prior_cloud(path) for path in prior_summary_paths]
    fused_cloud = fuse_point_clouds(clouds)
    input_point_count = int(len(fused_cloud.points_xyz))
    filtered_cloud, filter_summary = _filter_cloud(
        fused_cloud,
        outlier_filter=outlier_filter,
        outlier_keep_ratio=outlier_keep_ratio,
    )
    prior = fit_oriented_bbox(filtered_cloud)
    scene = export_scene_artifacts(filtered_cloud, prior, output_dir)

    summary_path = output_dir / "summary.json"
    summary = {
        "source": "fuse_object_priors",
        "prior_summary_paths": [str(path) for path in prior_summary_paths],
        "object_id": prior.object_id,
        "input_prior_count": len(prior_summary_paths),
        "input_point_count": input_point_count,
        "source_frame_ids": _unique_ints(fused_cloud.source_frame_ids),
        "bbox_type": "oriented",
        "center_xyz": prior.center_xyz.tolist(),
        "axes": prior.axes.tolist(),
        "dimensions_m": prior.dimensions_m.tolist(),
        "confidence": prior.confidence,
        "point_cloud_ply": scene["assets"]["point_cloud_ply"],
        "bbox_ply": scene["assets"]["bbox_ply"],
        "scene_manifest_json": scene["assets"]["scene_manifest_json"],
        "summary_json": str(summary_path),
    }
    summary.update(filter_summary)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _load_prior_cloud(summary_path: Path) -> PointCloudRecord:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    cloud_path = _resolve_path(summary_path, str(summary["point_cloud_ply"]))
    ply = read_ascii_ply(cloud_path)
    frame_id = int(summary["frame_id"])
    return PointCloudRecord(
        object_id=str(summary["object_id"]),
        points_xyz=np.asarray(ply.vertices, dtype=np.float32),
        source_frame_ids=(frame_id,),
    )


def _filter_cloud(
    cloud: PointCloudRecord,
    *,
    outlier_filter: str,
    outlier_keep_ratio: float,
) -> tuple[PointCloudRecord, dict[str, Any]]:
    if outlier_filter == "none":
        point_count = int(len(cloud.points_xyz))
        return cloud, {
            "outlier_filter": "none",
            "input_point_count": point_count,
            "filtered_point_count": point_count,
            "removed_point_count": 0,
        }
    if outlier_filter == "radial_percentile":
        return filter_point_cloud_radial_percentile(
            cloud,
            keep_ratio=outlier_keep_ratio,
        )
    raise ValueError("outlier_filter must be 'none' or 'radial_percentile'")


def _resolve_path(anchor_path: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    anchor_relative_path = anchor_path.parent / path
    if anchor_relative_path.exists():
        return anchor_relative_path
    return path


def _unique_ints(values: tuple[int, ...]) -> list[int]:
    return list(dict.fromkeys(int(value) for value in values))
