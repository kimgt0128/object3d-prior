from pathlib import Path

import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.visualization.export import export_point_cloud_ply


def test_export_point_cloud_ply_writes_ascii_ply(tmp_path: Path) -> None:
    cloud = PointCloudRecord(
        "object_001",
        np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]], dtype=np.float32),
        (0,),
    )
    output_path = tmp_path / "cloud.ply"

    export_point_cloud_ply(cloud, output_path)

    text = output_path.read_text()
    assert "element vertex 2" in text
    assert "0.000000 1.000000 2.000000" in text
