"""Video keyframe extraction pipeline helper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from object3d.capture.frame_source import FrameSource
from object3d.capture.pipeline import run_capture
from object3d.capture.records import CaptureMetadata


def run_video_keyframes(
    *,
    source: FrameSource,
    source_video: str,
    output_dir: Path,
    manifest_path: Path,
    target_fps: float,
) -> dict[str, Any]:
    """Sample video frames and write a reproducible keyframe manifest."""
    metadata = CaptureMetadata(
        object_name="room",
        measured_cm={},
        camera_mode="handheld_video",
        lighting="unknown",
        material="mixed_room",
        source_video=source_video,
        source_fps=source.source_fps,
    )
    manifest = run_capture(
        source=source,
        metadata=metadata,
        target_fps=target_fps,
        output_dir=output_dir,
        manifest_path=manifest_path,
    )
    if not manifest["frames"]:
        raise ValueError(
            f"video source did not produce any keyframes: {source_video}. "
            "Check the video path, permissions, codec, and target_fps."
        )
    frame_paths = [
        str((manifest_path.parent / frame["image_path"]).resolve())
        for frame in manifest["frames"]
    ]
    source_indices = [
        int(frame.get("camera_metadata", {}).get("source_index", frame["frame_id"]))
        for frame in manifest["frames"]
    ]
    return {
        "source": "video_keyframes",
        "source_video": source_video,
        "source_fps": float(source.source_fps),
        "target_fps": float(target_fps),
        "frame_count": len(frame_paths),
        "frame_ids": [int(frame["frame_id"]) for frame in manifest["frames"]],
        "source_indices": source_indices,
        "frame_paths": frame_paths,
        "manifest_json": str(manifest_path),
    }
