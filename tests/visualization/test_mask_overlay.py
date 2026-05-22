from pathlib import Path

import cv2
import numpy as np

from object3d.visualization.mask_overlay import export_mask_overlay


def test_export_mask_overlay_writes_overlay_png(tmp_path: Path) -> None:
    image = np.zeros((4, 5, 3), dtype=np.uint8)
    mask = np.zeros((4, 5), dtype=bool)
    mask[1:3, 2:5] = True
    output_path = tmp_path / "overlay.png"

    export_mask_overlay(image, mask, output_path)

    overlay = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
    assert overlay is not None
    assert overlay.shape == image.shape
    assert int(overlay[1, 2, 1]) > 0
    assert int(overlay[0, 0, 1]) == 0
