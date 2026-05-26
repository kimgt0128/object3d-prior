"""파일 기반 geometry adapter.

실제 MapAnything/VGGT/COLMAP 연동 전에는 각 모델 출력을 공통 `.npz`
형식으로 저장한 뒤 이 adapter로 `GeometryRecord`에 맞춘다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import numpy as np

from object3d.capture.records import FrameRecord
from object3d.contracts import GeometryRecord


REQUIRED_GEOMETRY_KEYS = ("depth_m", "intrinsics", "camera_to_world")


def load_geometry_npz(path: Path, frame: FrameRecord) -> GeometryRecord:
    """`.npz` geometry 파일을 `GeometryRecord`로 변환한다.

    Expected keys:
    - `depth_m`: `(H, W)` float depth map in meters
    - `intrinsics`: `(3, 3)` pinhole camera matrix
    - `camera_to_world`: `(4, 4)` camera-space to world-space transform

    `world_to_camera`는 일부 모델/도구에서 흔히 쓰는 이름이지만, 내부
    계약은 헷갈림을 막기 위해 `camera_to_world`만 받는다.
    """
    with np.load(path) as payload:
        arrays = {key: payload[key] for key in payload.files}

    _validate_required_keys(arrays)
    return GeometryRecord(
        frame_id=frame.frame_id,
        depth_m=np.asarray(arrays["depth_m"], dtype=np.float32),
        intrinsics=np.asarray(arrays["intrinsics"], dtype=np.float32),
        camera_to_world=np.asarray(arrays["camera_to_world"], dtype=np.float32),
    )


def _validate_required_keys(arrays: Mapping[str, np.ndarray]) -> None:
    missing = [key for key in REQUIRED_GEOMETRY_KEYS if key not in arrays]
    if missing:
        required = ", ".join(REQUIRED_GEOMETRY_KEYS)
        present = ", ".join(sorted(arrays)) or "<none>"
        raise ValueError(
            f"geometry npz must contain {required}; missing {missing}; present keys: {present}"
        )
