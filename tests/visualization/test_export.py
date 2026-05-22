from pathlib import Path

import numpy as np

from object3d.contracts import ObjectPrior, PointCloudRecord
from object3d.visualization.export import (
    export_point_cloud_ply,
    export_oriented_bbox_ply,
    export_scene_artifacts,
    oriented_bbox_corners,
)


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


def test_oriented_bbox_corners_from_prior() -> None:
    prior = ObjectPrior(
        object_id="object_001",
        center_xyz=np.array([1.0, 2.0, 3.0], dtype=np.float32),
        axes=np.eye(3, dtype=np.float32),
        dimensions_m=np.array([2.0, 4.0, 6.0], dtype=np.float32),
        confidence=0.9,
    )

    corners = oriented_bbox_corners(prior)

    assert corners.shape == (8, 3)
    np.testing.assert_allclose(corners.min(axis=0), np.array([0.0, 0.0, 0.0]))
    np.testing.assert_allclose(corners.max(axis=0), np.array([2.0, 4.0, 6.0]))


def test_export_oriented_bbox_ply_writes_vertices_and_edges(tmp_path: Path) -> None:
    prior = ObjectPrior(
        object_id="object_001",
        center_xyz=np.zeros(3, dtype=np.float32),
        axes=np.eye(3, dtype=np.float32),
        dimensions_m=np.array([2.0, 2.0, 2.0], dtype=np.float32),
        confidence=1.0,
    )
    output_path = tmp_path / "bbox.ply"

    export_oriented_bbox_ply(prior, output_path)

    text = output_path.read_text()
    assert "element vertex 8" in text
    assert "element edge 12" in text
    assert "property int vertex1" in text


def test_export_scene_artifacts_writes_manifest_and_assets(tmp_path: Path) -> None:
    cloud = PointCloudRecord(
        "object_001",
        np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32),
        (0, 1),
    )
    prior = ObjectPrior(
        object_id="object_001",
        center_xyz=np.array([0.5, 0.5, 0.5], dtype=np.float32),
        axes=np.eye(3, dtype=np.float32),
        dimensions_m=np.array([1.0, 1.0, 1.0], dtype=np.float32),
        confidence=1.0,
    )

    manifest = export_scene_artifacts(cloud, prior, tmp_path)

    assert Path(manifest["assets"]["point_cloud_ply"]).exists()
    assert Path(manifest["assets"]["bbox_ply"]).exists()
    assert Path(manifest["assets"]["scene_manifest_json"]).exists()
    assert manifest["object_id"] == "object_001"
    assert manifest["bbox_type"] == "oriented"
    assert manifest["source_frame_ids"] == [0, 1]
