"""Batch segmentation helper for sampled keyframe manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from object3d.capture.manifest import read_manifest
from object3d.pipeline.run_manual_segmentation import run_manual_segmentation


def run_segment_keyframes(
    *,
    frame_manifest_path: Path,
    prompt_manifest_path: Path,
    output_dir: Path,
    backend: str = "manual",
    checkpoint_path: Path | None = None,
    config_path: Path | None = None,
    device: str = "cpu",
    predictor_loader=None,
) -> dict[str, Any]:
    """Run segmentation for object/frame prompts listed in a prompt manifest."""
    frame_manifest = read_manifest(frame_manifest_path)
    prompt_manifest = _load_json(prompt_manifest_path)
    frames_by_id = {
        int(frame["frame_id"]): frame
        for frame in frame_manifest.get("frames", [])
    }
    objects = list(prompt_manifest.get("objects", []))
    if not objects:
        raise ValueError("prompt manifest must contain at least one object")

    output_dir.mkdir(parents=True, exist_ok=True)
    object_summaries = []
    segmentation_count = 0
    for object_prompt in objects:
        object_id = str(object_prompt["object_id"])
        frame_prompts = list(object_prompt.get("frames", []))
        if not frame_prompts:
            raise ValueError(f"object {object_id} must contain at least one frame")

        frame_summaries = []
        for frame_prompt in frame_prompts:
            frame_id = int(frame_prompt["frame_id"])
            if frame_id not in frames_by_id:
                raise ValueError(f"frame_id {frame_id} was not found in frame manifest")

            frame = frames_by_id[frame_id]
            image_path = _resolve_path(
                frame_manifest_path,
                str(frame["image_path"]),
            )
            prompt_path = _resolve_path(
                prompt_manifest_path,
                str(frame_prompt["prompt_json"]),
            )
            segmentation = run_manual_segmentation(
                image_path=image_path,
                prompt_json_path=prompt_path,
                output_dir=output_dir / object_id / f"frame_{frame_id:06d}",
                object_id=object_id,
                frame_id=frame_id,
                backend=backend,
                checkpoint_path=checkpoint_path,
                config_path=config_path,
                device=device,
                predictor_loader=predictor_loader,
            )
            segmentation.update(
                {
                    "timestamp_s": float(frame.get("timestamp_s", 0.0)),
                    "source_index": int(
                        frame.get("camera_metadata", {}).get("source_index", frame_id)
                    ),
                }
            )
            frame_summaries.append(segmentation)
            segmentation_count += 1

        object_summaries.append(
            {
                "object_id": object_id,
                "frame_count": len(frame_summaries),
                "frames": frame_summaries,
            }
        )

    summary_path = output_dir / "segmentation_batch.summary.json"
    summary = {
        "source": "segment_keyframes",
        "frame_manifest_json": str(frame_manifest_path),
        "prompt_manifest_json": str(prompt_manifest_path),
        "output_dir": str(output_dir),
        "backend": backend,
        "device": device,
        "object_count": len(object_summaries),
        "segmentation_count": segmentation_count,
        "objects": object_summaries,
        "summary_json": str(summary_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(anchor_path: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    anchor_relative_path = anchor_path.parent / path
    if anchor_relative_path.exists():
        return anchor_relative_path
    return path
