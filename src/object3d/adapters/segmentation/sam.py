"""SAM/SAM2 predictor 출력을 `MaskRecord`로 정규화하는 adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from object3d.capture.records import FrameRecord
from object3d.contracts import MaskRecord


class OptionalSegmentationDependencyError(ImportError):
    """선택 segmentation dependency가 없을 때 발생하는 에러."""


@dataclass(frozen=True)
class SamPrompt:
    """SAM 계열 predictor에 전달할 최소 prompt contract."""

    box_xyxy: Optional[Tuple[float, float, float, float]] = None
    point_coords_xy: Tuple[Tuple[float, float], ...] = ()
    point_labels: Tuple[int, ...] = ()
    multimask_output: bool = True

    def __post_init__(self) -> None:
        if self.box_xyxy is None and not self.point_coords_xy:
            raise ValueError("SamPrompt requires a box or points")
        if len(self.point_coords_xy) != len(self.point_labels):
            raise ValueError("point_coords_xy and point_labels must have the same length")
        if any(label not in (0, 1) for label in self.point_labels):
            raise ValueError("point_labels must contain only 0 or 1")


def predict_mask(
    frame: FrameRecord,
    *,
    image: NDArray[np.uint8],
    object_id: str,
    predictor: Any,
    prompt: SamPrompt,
) -> MaskRecord:
    """주입된 SAM-like predictor로 mask를 예측하고 `MaskRecord`로 변환한다."""
    predictor.set_image(image)
    masks, scores, _ = predictor.predict(
        box=_box_array(prompt),
        point_coords=_point_coords_array(prompt),
        point_labels=_point_labels_array(prompt),
        multimask_output=prompt.multimask_output,
    )
    selected_index = int(np.argmax(scores))
    selected_mask = np.asarray(masks[selected_index], dtype=bool)
    confidence = float(scores[selected_index])
    return MaskRecord(
        frame_id=frame.frame_id,
        object_id=object_id,
        mask=selected_mask,
        confidence=confidence,
    )


def load_sam_predictor(
    *,
    backend: Literal["sam", "sam2"],
    checkpoint_path: Path,
    model_type: Optional[str] = None,
    config_path: Optional[Path] = None,
    device: str = "cpu",
) -> Any:
    """SAM 또는 SAM2 predictor를 lazy import로 생성한다.

    실제 모델 dependency는 기본 설치에 포함하지 않는다. 이 함수는 후속
    실모델 연동 단계에서만 호출한다.
    """
    if backend == "sam":
        if model_type is None:
            raise ValueError("model_type is required for sam backend")
        return _load_sam1_predictor(
            checkpoint_path=checkpoint_path,
            model_type=model_type,
            device=device,
        )
    if backend == "sam2":
        if config_path is None:
            raise ValueError("config_path is required for sam2 backend")
        return _load_sam2_predictor(
            checkpoint_path=checkpoint_path,
            config_path=config_path,
            device=device,
        )
    raise ValueError("backend must be 'sam' or 'sam2'")


def _box_array(prompt: SamPrompt) -> Optional[NDArray[np.float32]]:
    if prompt.box_xyxy is None:
        return None
    return np.asarray(prompt.box_xyxy, dtype=np.float32)


def _point_coords_array(prompt: SamPrompt) -> Optional[NDArray[np.float32]]:
    if not prompt.point_coords_xy:
        return None
    return np.asarray(prompt.point_coords_xy, dtype=np.float32)


def _point_labels_array(prompt: SamPrompt) -> Optional[NDArray[np.int64]]:
    if not prompt.point_labels:
        return None
    return np.asarray(prompt.point_labels, dtype=np.int64)


def _load_sam1_predictor(
    *,
    checkpoint_path: Path,
    model_type: str,
    device: str,
) -> Any:
    try:
        from segment_anything import SamPredictor, sam_model_registry
    except ImportError as error:
        raise OptionalSegmentationDependencyError(
            "segment_anything is required for backend='sam'. "
            "Install SAM dependencies before calling load_sam_predictor()."
        ) from error

    model = sam_model_registry[model_type](checkpoint=str(checkpoint_path))
    model.to(device=device)
    return SamPredictor(model)


def _load_sam2_predictor(
    *,
    checkpoint_path: Path,
    config_path: Path,
    device: str,
) -> Any:
    try:
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
    except ImportError as error:
        raise OptionalSegmentationDependencyError(
            "sam2 is required for backend='sam2'. "
            "Install SAM2 dependencies before calling load_sam_predictor()."
        ) from error

    model = build_sam2(
        _normalize_sam2_model_cfg(config_path),
        str(checkpoint_path),
        device=device,
    )
    return SAM2ImagePredictor(model)


def _normalize_sam2_model_cfg(config_path: Path) -> str:
    """SAM2 package 내부 config 절대경로를 Hydra 상대경로로 변환한다."""
    if not config_path.is_absolute():
        return config_path.as_posix()

    try:
        import sam2
    except ImportError:
        return config_path.as_posix()

    package_root = Path(sam2.__file__).resolve().parent
    try:
        return config_path.resolve().relative_to(package_root).as_posix()
    except ValueError:
        return config_path.as_posix()
