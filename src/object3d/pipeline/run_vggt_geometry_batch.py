"""VGGT geometry batch helper for sampled keyframe manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Protocol

import numpy as np

from object3d.adapters.geometry.vggt import save_vggt_geometry_npz
from object3d.capture.manifest import read_manifest
from object3d.pipeline.run_vggt_geometry import _run_vggt_prediction


class VggtBatchPredictionRunner(Protocol):
    """Callable contract for creating one VGGT prediction from many images."""

    def __call__(
        self,
        *,
        image_paths: tuple[Path, ...],
        device: str,
        model_id: str,
    ) -> Mapping[str, Any]:
        """Return raw VGGT prediction arrays for all image paths."""


def run_vggt_geometry_batch(
    *,
    manifest_path: Path,
    output_dir: Path,
    device: str = "cpu",
    model_id: str = "facebook/VGGT-1B",
    max_frames: int | None = 12,
    runner: VggtBatchPredictionRunner | None = None,
) -> dict[str, Any]:
    """Run VGGT once for keyframes and save per-frame geometry artifacts."""
    manifest = read_manifest(manifest_path)
    frames = list(manifest.get("frames", []))
    if max_frames is not None:
        if max_frames <= 0:
            raise ValueError("max_frames must be positive when provided")
        frames = frames[:max_frames]
    if not frames:
        raise ValueError("frame manifest must contain at least one frame")

    image_paths = tuple(
        _resolve_manifest_path(manifest_path, str(frame["image_path"]))
        for frame in frames
    )
    _validate_image_paths_are_readable(image_paths)

    prediction_runner = runner or _run_vggt_prediction
    prediction = prediction_runner(
        image_paths=image_paths,
        device=device,
        model_id=model_id,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    geometries = []
    for frame_index, (frame, image_path) in enumerate(
        zip(frames, image_paths, strict=True)
    ):
        frame_id = int(frame["frame_id"])
        geometry_path = output_dir / f"frame_{frame_id:06d}" / "geometry.npz"
        geometry_summary = save_vggt_geometry_npz(
            prediction,
            output_path=geometry_path,
            frame_index=frame_index,
        )
        with np.load(geometry_path) as payload:
            geometry_depth_shape = list(payload["depth_m"].shape)
        geometries.append(
            {
                "frame_id": frame_id,
                "frame_index": frame_index,
                "image_path": str(image_path),
                "timestamp_s": float(frame.get("timestamp_s", 0.0)),
                "source_index": int(
                    frame.get("camera_metadata", {}).get("source_index", frame_id)
                ),
                "geometry_depth_shape": geometry_depth_shape,
                **geometry_summary,
            }
        )

    summary_path = output_dir / "geometry_batch.summary.json"
    summary = {
        "source": "vggt_geometry_batch",
        "manifest_json": str(manifest_path),
        "output_dir": str(output_dir),
        "device": device,
        "model_id": model_id,
        "max_frames": max_frames,
        "frame_count": len(frames),
        "geometry_count": len(geometries),
        "geometries": geometries,
        "summary_json": str(summary_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _resolve_manifest_path(manifest_path: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    manifest_relative_path = manifest_path.parent / path
    if manifest_relative_path.exists():
        return manifest_relative_path
    return path


def _validate_image_paths_are_readable(image_paths: tuple[Path, ...]) -> None:
    for image_path in image_paths:
        if not image_path.exists():
            raise FileNotFoundError(
                f"input keyframe not found: {image_path}. "
                "Run video_keyframes first and check the frame manifest paths."
            )
        try:
            with image_path.open("rb") as handle:
                handle.read(1)
        except PermissionError as error:
            raise PermissionError(
                f"cannot read keyframe: {image_path}. "
                "Copy videos/keyframes under this workspace or grant terminal access."
            ) from error
