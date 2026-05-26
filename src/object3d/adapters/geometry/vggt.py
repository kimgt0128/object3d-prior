"""VGGT prediction을 file geometry contract로 변환하는 adapter skeleton."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np


class OptionalGeometryDependencyError(ImportError):
    """선택 geometry dependency가 없을 때 발생하는 에러."""


def save_vggt_geometry_npz(
    prediction: Mapping[str, Any],
    *,
    output_path: Path,
    frame_index: int = 0,
) -> dict[str, Any]:
    """VGGT prediction 한 frame을 `geometry.npz` 계약으로 저장한다.

    VGGT 공식 사용 예시는 extrinsic을 OpenCV convention의 camera-from-world로
    설명한다. 내부 계약은 camera-to-world만 받으므로 역행렬로 변환한다.
    """
    depth_m = _select_frame_array(
        prediction,
        keys=("depth_map", "depth_maps"),
        frame_index=frame_index,
        label="depth",
    )
    depth_m = _as_depth_map(depth_m)
    intrinsics = _select_frame_array(
        prediction,
        keys=("intrinsic", "intrinsics"),
        frame_index=frame_index,
        label="intrinsics",
    )
    world_to_camera = _select_frame_array(
        prediction,
        keys=("extrinsic", "extrinsics"),
        frame_index=frame_index,
        label="extrinsics",
    )
    camera_to_world = np.linalg.inv(_as_homogeneous_transform(world_to_camera))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output_path,
        depth_m=np.asarray(depth_m, dtype=np.float32),
        intrinsics=np.asarray(intrinsics, dtype=np.float32),
        camera_to_world=np.asarray(camera_to_world, dtype=np.float32),
    )
    return {
        "geometry_source": "vggt",
        "geometry_npz": str(output_path),
        "frame_index": int(frame_index),
    }


def load_vggt_model(
    *,
    model_id: str = "facebook/VGGT-1B",
    device: str = "cpu",
) -> Any:
    """VGGT model을 lazy import로 생성한다.

    실제 dependency와 checkpoint download는 기본 테스트에 강제하지 않는다.
    """
    try:
        from vggt.models.vggt import VGGT
    except ImportError as error:
        raise OptionalGeometryDependencyError(
            "vggt is required to load a VGGT geometry model. "
            "Install VGGT dependencies before calling load_vggt_model()."
        ) from error

    return VGGT.from_pretrained(model_id).to(device)


def _select_frame_array(
    prediction: Mapping[str, Any],
    *,
    keys: tuple[str, ...],
    frame_index: int,
    label: str,
) -> np.ndarray:
    for key in keys:
        if key in prediction:
            return _frame_slice(np.asarray(prediction[key]), frame_index=frame_index)
    joined_keys = ", ".join(keys)
    raise ValueError(f"VGGT prediction must contain {label} key: {joined_keys}")


def _frame_slice(array: np.ndarray, *, frame_index: int) -> np.ndarray:
    if array.ndim >= 3:
        return np.asarray(array[frame_index])
    return np.asarray(array)


def _as_homogeneous_transform(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.shape == (4, 4):
        return matrix
    if matrix.shape == (3, 4):
        transform = np.eye(4, dtype=np.float32)
        transform[:3, :] = matrix
        return transform
    raise ValueError("VGGT extrinsic must have shape (4, 4) or (3, 4)")


def _as_depth_map(depth: np.ndarray) -> np.ndarray:
    depth = np.asarray(depth, dtype=np.float32)
    if depth.ndim == 3 and depth.shape[-1] == 1:
        depth = depth[..., 0]
    if depth.ndim != 2:
        raise ValueError("VGGT depth must have shape (H, W) or (H, W, 1)")
    return depth
