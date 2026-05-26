"""segmentation mask 산출물을 3D object prior 산출물로 변환한다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from object3d.adapters.geometry.file import load_geometry_npz
from object3d.adapters.geometry.mock import make_planar_mock_geometry
from object3d.capture.records import FrameRecord
from object3d.contracts import GeometryRecord
from object3d.contracts import MaskRecord
from object3d.geometry.backprojection import backproject_masked_points
from object3d.priors.bbox import fit_oriented_bbox
from object3d.visualization.export import export_scene_artifacts


def run_prior_from_mask(
    *,
    segmentation_summary_path: Path,
    output_dir: Path,
    depth_m: float,
    geometry_npz_path: Path | None = None,
) -> dict[str, Any]:
    """segmentation summary의 mask를 3D object prior로 변환한다."""
    if geometry_npz_path is None and depth_m <= 0:
        raise ValueError("depth_m must be positive")

    segmentation_summary = _load_json(segmentation_summary_path)
    mask_path = _resolve_path(segmentation_summary_path, segmentation_summary["mask_npy"])
    mask_array = np.load(mask_path)
    mask = MaskRecord(
        frame_id=int(segmentation_summary["frame_id"]),
        object_id=str(segmentation_summary["object_id"]),
        mask=np.asarray(mask_array, dtype=bool),
        confidence=float(segmentation_summary["confidence"]),
    )
    frame = FrameRecord(
        frame_id=mask.frame_id,
        image_path=str(segmentation_summary.get("image_path", "")),
        timestamp_s=0.0,
    )
    geometry, geometry_summary = _load_geometry(
        frame=frame,
        image_shape=mask.mask.shape,
        depth_m=depth_m,
        geometry_npz_path=geometry_npz_path,
    )
    cloud = backproject_masked_points(mask, geometry)
    prior = fit_oriented_bbox(cloud)

    output_dir.mkdir(parents=True, exist_ok=True)
    scene = export_scene_artifacts(cloud, prior, output_dir)
    summary_path = output_dir / "summary.json"
    summary = {
        "source": "segmentation_summary",
        "segmentation_summary": str(segmentation_summary_path),
        "backend": segmentation_summary.get("backend"),
        "object_id": prior.object_id,
        "frame_id": mask.frame_id,
        "mask_npy": str(mask_path),
        "mask_pixels": int(mask.mask.sum()),
        "point_count": int(len(cloud.points_xyz)),
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
    summary.update(geometry_summary)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(anchor_path: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute() or path.exists():
        return path
    return anchor_path.parent / path


def _load_geometry(
    *,
    frame: FrameRecord,
    image_shape: tuple[int, int],
    depth_m: float,
    geometry_npz_path: Path | None,
) -> tuple[GeometryRecord, dict[str, Any]]:
    if geometry_npz_path is not None:
        geometry = load_geometry_npz(geometry_npz_path, frame)
        return geometry, {
            "geometry_source": "npz",
            "geometry_npz": str(geometry_npz_path),
        }

    geometry = make_planar_mock_geometry(
        frame,
        image_shape=image_shape,
        depth_m=depth_m,
    )
    return geometry, {
        "geometry_source": "mock",
        "depth_m": float(depth_m),
    }
