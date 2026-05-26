from pathlib import Path

import cv2
import numpy as np

from object3d.visualization.contact_sheet import ContactSheetItem, export_contact_sheet


def test_export_contact_sheet_writes_labeled_grid(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    output_path = tmp_path / "sheet.jpg"
    cv2.imwrite(str(first), np.full((20, 30, 3), (255, 0, 0), dtype=np.uint8))
    cv2.imwrite(str(second), np.full((10, 20, 3), (0, 255, 0), dtype=np.uint8))

    export_contact_sheet(
        [
            ContactSheetItem(first, "manual box"),
            ContactSheetItem(second, "SAM2 mask"),
        ],
        output_path,
        columns=2,
        cell_width=40,
    )

    sheet = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
    assert sheet is not None
    assert sheet.shape == (70, 80, 3)
    assert int(sheet[10, 10, 0]) > 200
    assert int(sheet[10, 50, 1]) > 200
