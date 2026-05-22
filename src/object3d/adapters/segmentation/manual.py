"""수동 prompt를 SAM-like segmentation adapter로 흘려보내는 경량 도구."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from object3d.adapters.segmentation.sam import SamPrompt


class ManualBoxPredictor:
    """SAM predictor 없이 box/point prompt를 mask로 바꾸는 테스트용 predictor."""

    def __init__(self) -> None:
        self._image_shape: tuple[int, int] | None = None

    def set_image(self, image: NDArray[np.uint8]) -> None:
        if image.ndim != 3:
            raise ValueError("image must have shape (H, W, C)")
        height, width = image.shape[:2]
        self._image_shape = (height, width)

    def predict(
        self,
        *,
        box: NDArray[np.float32] | None,
        point_coords: NDArray[np.float32] | None,
        point_labels: NDArray[np.int64] | None,
        multimask_output: bool,
    ) -> tuple[NDArray[np.bool_], NDArray[np.float32], None]:
        del multimask_output
        if self._image_shape is None:
            raise ValueError("set_image() must be called before predict()")

        height, width = self._image_shape
        mask = np.zeros((height, width), dtype=bool)
        if box is not None:
            x0, y0, x1, y1 = _clip_box(box, width=width, height=height)
            mask[y0:y1, x0:x1] = True
        elif point_coords is not None and point_labels is not None:
            _apply_point_prompt(mask, point_coords, point_labels)
        else:
            raise ValueError("manual predictor requires a box or points")

        return np.expand_dims(mask, axis=0), np.array([1.0], dtype=np.float32), None


def load_prompt_json(prompt_path: Path) -> SamPrompt:
    """prompt JSON 파일을 `SamPrompt`로 변환한다."""
    payload: dict[str, Any] = json.loads(prompt_path.read_text(encoding="utf-8"))
    box = payload.get("box_xyxy")
    points = payload.get("point_coords_xy", [])
    labels = payload.get("point_labels", [])
    return SamPrompt(
        box_xyxy=tuple(float(value) for value in box) if box is not None else None,
        point_coords_xy=tuple(
            (float(point[0]), float(point[1])) for point in points
        ),
        point_labels=tuple(int(label) for label in labels),
        multimask_output=bool(payload.get("multimask_output", True)),
    )


def _clip_box(
    box: NDArray[np.float32],
    *,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box.tolist()
    left = int(np.clip(np.floor(x0), 0, width))
    top = int(np.clip(np.floor(y0), 0, height))
    right = int(np.clip(np.ceil(x1), 0, width))
    bottom = int(np.clip(np.ceil(y1), 0, height))
    if right <= left or bottom <= top:
        raise ValueError("box must cover at least one pixel")
    return left, top, right, bottom


def _apply_point_prompt(
    mask: NDArray[np.bool_],
    point_coords: NDArray[np.float32],
    point_labels: NDArray[np.int64],
) -> None:
    height, width = mask.shape
    for (x_coord, y_coord), label in zip(point_coords, point_labels):
        if int(label) != 1:
            continue
        x = int(np.clip(round(float(x_coord)), 0, width - 1))
        y = int(np.clip(round(float(y_coord)), 0, height - 1))
        mask[y, x] = True
