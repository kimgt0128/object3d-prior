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
from object3d.reconstruction.mask_cleanup import clean_mask_for_object_prior
from object3d.reconstruction.mask_cleanup import MASK_CLEANUP_MODES
from object3d.reconstruction.outlier_filter import (
    filter_point_cloud_radial_percentile,
)
from object3d.visualization.export import export_scene_artifacts


def run_prior_from_mask(
    *,
    segmentation_summary_path: Path,
    output_dir: Path,
    depth_m: float,
    geometry_npz_path: Path | None = None,
    mask_cleanup: str = "none",
    mask_erode_pixels: int = 0,
    outlier_filter: str = "none",
    outlier_keep_ratio: float = 0.95,
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
    output_dir.mkdir(parents=True, exist_ok=True)
    mask, mask_summary = _align_mask_to_geometry(
        mask=mask,
        geometry=geometry,
        source_mask_path=mask_path,
        output_dir=output_dir,
    )
    mask, cleanup_summary = _clean_mask(
        mask=mask,
        current_mask_path=Path(mask_summary["mask_npy"]),
        output_dir=output_dir,
        mask_cleanup=mask_cleanup,
        mask_erode_pixels=mask_erode_pixels,
    )
    cloud = backproject_masked_points(mask, geometry)
    cloud, outlier_summary = _filter_cloud(
        cloud=cloud,
        outlier_filter=outlier_filter,
        outlier_keep_ratio=outlier_keep_ratio,
    )
    prior = fit_oriented_bbox(cloud)

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
    summary.update(mask_summary)
    summary.update(cleanup_summary)
    summary.update(geometry_summary)
    summary.update(outlier_summary)
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


def _filter_cloud(
    *,
    cloud,
    outlier_filter: str,
    outlier_keep_ratio: float,
):
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


def _clean_mask(
    *,
    mask: MaskRecord,
    current_mask_path: Path,
    output_dir: Path,
    mask_cleanup: str,
    mask_erode_pixels: int,
) -> tuple[MaskRecord, dict[str, Any]]:
    if mask_cleanup not in MASK_CLEANUP_MODES:
        raise ValueError("mask_cleanup must be 'none' or 'largest_component'")

    cleaned_mask, cleanup_summary = clean_mask_for_object_prior(
        mask.mask,
        mode=mask_cleanup,
        erode_pixels=mask_erode_pixels,
    )
    should_save_cleaned_mask = mask_cleanup != "none" or mask_erode_pixels > 0
    if not should_save_cleaned_mask:
        return mask, {
            **cleanup_summary,
            "mask_npy": str(current_mask_path),
        }

    cleaned_mask_path = output_dir / "mask_cleaned.npy"
    np.save(cleaned_mask_path, cleaned_mask)
    return (
        MaskRecord(
            frame_id=mask.frame_id,
            object_id=mask.object_id,
            mask=cleaned_mask,
            confidence=mask.confidence,
        ),
        {
            **cleanup_summary,
            "pre_cleanup_mask_npy": str(current_mask_path),
            "cleaned_mask_npy": str(cleaned_mask_path),
            "mask_npy": str(cleaned_mask_path),
        },
    )


def _align_mask_to_geometry(
    *,
    mask: MaskRecord,
    geometry: GeometryRecord,
    source_mask_path: Path,
    output_dir: Path,
) -> tuple[MaskRecord, dict[str, Any]]:
    input_shape = tuple(int(value) for value in mask.mask.shape)
    geometry_shape = tuple(int(value) for value in geometry.depth_m.shape)
    if input_shape == geometry_shape:
        return mask, {
            "mask_alignment": "native",
            "mask_npy": str(source_mask_path),
            "input_mask_shape": list(input_shape),
            "geometry_depth_shape": list(geometry_shape),
            "effective_mask_shape": list(input_shape),
            "source_mask_npy": str(source_mask_path),
        }

    resized_mask = _resize_bool_mask_nearest(mask.mask, geometry_shape)
    resized_mask_path = output_dir / "mask_geometry_shape.npy"
    np.save(resized_mask_path, resized_mask)
    return (
        MaskRecord(
            frame_id=mask.frame_id,
            object_id=mask.object_id,
            mask=resized_mask,
            confidence=mask.confidence,
        ),
        {
            "mask_alignment": "resized_to_geometry",
            "mask_npy": str(resized_mask_path),
            "input_mask_shape": list(input_shape),
            "geometry_depth_shape": list(geometry_shape),
            "effective_mask_shape": list(geometry_shape),
            "source_mask_npy": str(source_mask_path),
            "resized_mask_npy": str(resized_mask_path),
        },
    )


def _resize_bool_mask_nearest(
    mask: np.ndarray,
    target_shape: tuple[int, int],
) -> np.ndarray:
    source_height, source_width = mask.shape
    target_height, target_width = target_shape
    if target_height <= 0 or target_width <= 0:
        raise ValueError("target mask shape must be positive")

    y_indices = np.minimum(
        (np.arange(target_height) * source_height / target_height).astype(int),
        source_height - 1,
    )
    x_indices = np.minimum(
        (np.arange(target_width) * source_width / target_width).astype(int),
        source_width - 1,
    )
    return np.asarray(mask[np.ix_(y_indices, x_indices)], dtype=bool)
