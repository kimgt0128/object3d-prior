"""Small contact sheet export helpers for validation artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


@dataclass(frozen=True)
class ContactSheetItem:
    image_path: Path
    label: str


def export_contact_sheet(
    items: Sequence[ContactSheetItem],
    output_path: Path,
    *,
    columns: int = 2,
    cell_width: int = 420,
    label_height: int = 30,
) -> None:
    """Write labeled image thumbnails as a compact validation contact sheet."""
    if not items:
        raise ValueError("contact sheet requires at least one item")
    if columns <= 0:
        raise ValueError("columns must be positive")
    if cell_width <= 0:
        raise ValueError("cell_width must be positive")
    if label_height < 0:
        raise ValueError("label_height must be non-negative")

    rows = int(np.ceil(len(items) / columns))
    cell_height = cell_width + label_height
    sheet = np.full(
        (rows * cell_height, columns * cell_width, 3),
        255,
        dtype=np.uint8,
    )

    for index, item in enumerate(items):
        image = cv2.imread(str(item.image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"failed to read contact sheet image: {item.image_path}")
        row = index // columns
        column = index % columns
        x0 = column * cell_width
        y0 = row * cell_height
        thumbnail = _fit_image_to_square(image, cell_width)
        thumb_y = y0 + (cell_width - thumbnail.shape[0]) // 2
        thumb_x = x0 + (cell_width - thumbnail.shape[1]) // 2
        sheet[
            thumb_y : thumb_y + thumbnail.shape[0],
            thumb_x : thumb_x + thumbnail.shape[1],
        ] = thumbnail
        if label_height:
            cv2.putText(
                sheet,
                item.label,
                (x0 + 8, y0 + cell_width + min(22, label_height - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (32, 32, 32),
                1,
                cv2.LINE_AA,
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
    if not cv2.imwrite(str(output_path), sheet, encode_params):
        raise ValueError(f"failed to write contact sheet: {output_path}")


def _fit_image_to_square(image: np.ndarray, size: int) -> np.ndarray:
    height, width = image.shape[:2]
    scale = min(size / width, size / height)
    resized_width = max(1, int(round(width * scale)))
    resized_height = max(1, int(round(height * scale)))
    return cv2.resize(
        image,
        (resized_width, resized_height),
        interpolation=cv2.INTER_AREA,
    )
