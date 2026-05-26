"""VGGT prediction을 project geometry artifact로 저장하는 pipeline helper."""

from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

import numpy as np

from object3d.adapters.geometry.vggt import (
    OptionalGeometryDependencyError,
    load_vggt_model,
    save_vggt_geometry_npz,
)


class VggtPredictionRunner(Protocol):
    """VGGT prediction을 만드는 callable 계약."""

    def __call__(
        self,
        *,
        image_paths: tuple[Path, ...],
        device: str,
        model_id: str,
    ) -> Mapping[str, Any]:
        """이미지 목록을 받아 VGGT raw prediction mapping을 반환한다."""


def run_vggt_geometry(
    *,
    image_paths: Sequence[Path],
    output_path: Path,
    frame_index: int = 0,
    device: str = "cpu",
    model_id: str = "facebook/VGGT-1B",
    runner: VggtPredictionRunner | None = None,
) -> dict[str, Any]:
    """이미지 입력을 VGGT geometry `.npz` artifact로 변환한다."""
    normalized_image_paths = tuple(Path(path) for path in image_paths)
    if not normalized_image_paths:
        raise ValueError("run_vggt_geometry requires at least one image path")
    _validate_image_paths_are_readable(normalized_image_paths)

    prediction_runner = runner or _run_vggt_prediction
    prediction = prediction_runner(
        image_paths=normalized_image_paths,
        device=device,
        model_id=model_id,
    )
    geometry_summary = save_vggt_geometry_npz(
        prediction,
        output_path=output_path,
        frame_index=frame_index,
    )
    with np.load(output_path) as geometry_payload:
        geometry_depth_shape = list(geometry_payload["depth_m"].shape)
    summary_path = output_path.with_suffix(".summary.json")
    summary = {
        "source": "vggt_geometry",
        "image_paths": [str(path) for path in normalized_image_paths],
        "image_count": len(normalized_image_paths),
        "device": device,
        "model_id": model_id,
        "geometry_depth_shape": geometry_depth_shape,
        "summary_json": str(summary_path),
    }
    summary.update(geometry_summary)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _run_vggt_prediction(
    *,
    image_paths: tuple[Path, ...],
    device: str,
    model_id: str,
) -> Mapping[str, Any]:
    try:
        import torch
        from vggt.utils.load_fn import load_and_preprocess_images
        from vggt.utils.pose_enc import pose_encoding_to_extri_intri
    except ImportError as error:
        raise OptionalGeometryDependencyError(
            "vggt and torch are required to run VGGT geometry inference. "
            "Install VGGT dependencies or pass an injected runner for tests."
        ) from error

    model = load_vggt_model(model_id=model_id, device=device)
    model.eval()
    images = load_and_preprocess_images([str(path) for path in image_paths]).to(device)
    if len(images.shape) == 4:
        images = images[None]

    with torch.no_grad():
        with _autocast_context(torch, device):
            aggregated_tokens_list, patch_start_idx = model.aggregator(images)
            pose_enc = model.camera_head(aggregated_tokens_list)[-1]
            extrinsic, intrinsic = pose_encoding_to_extri_intri(
                pose_enc,
                images.shape[-2:],
            )
            depth, _depth_conf = model.depth_head(
                aggregated_tokens_list,
                images=images,
                patch_start_idx=patch_start_idx,
            )

    return {
        "depth_map": _to_numpy_without_batch(depth),
        "intrinsic": _to_numpy_without_batch(intrinsic),
        "extrinsic": _to_numpy_without_batch(extrinsic),
    }


def _validate_image_paths_are_readable(image_paths: tuple[Path, ...]) -> None:
    for image_path in image_paths:
        if not image_path.exists():
            raise FileNotFoundError(
                f"input image not found: {image_path}. "
                "Run `ls` on the parent directory and make sure the variable points "
                "to the copied workspace file, not an old Downloads path."
            )
        try:
            with image_path.open("rb") as handle:
                handle.read(1)
        except PermissionError as error:
            raise PermissionError(
                f"cannot read input image: {image_path}. "
                "On macOS, copy it under this workspace, for example under "
                "`outputs/.../input/`, or grant Full Disk Access to the terminal app."
            ) from error


def _autocast_context(torch: Any, device: str) -> Any:
    if not device.startswith("cuda") or not torch.cuda.is_available():
        return nullcontext()
    capability = torch.cuda.get_device_capability()
    dtype = torch.bfloat16 if capability[0] >= 8 else torch.float16
    return torch.cuda.amp.autocast(dtype=dtype)


def _to_numpy_without_batch(value: Any) -> np.ndarray:
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    array = np.asarray(value)
    if array.ndim >= 1 and array.shape[0] == 1:
        return array[0]
    return array
