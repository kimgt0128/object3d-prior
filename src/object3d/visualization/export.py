"""Open3D/Rerun 연동 전 사용할 수 있는 경량 export 함수."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from object3d.contracts import ObjectPrior, PointCloudRecord


BBOX_EDGE_INDICES: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (0, 4),
    (1, 3),
    (1, 5),
    (2, 3),
    (2, 6),
    (3, 7),
    (4, 5),
    (4, 6),
    (5, 7),
    (6, 7),
)


def export_point_cloud_ply(cloud: PointCloudRecord, output_path: Path) -> None:
    """객체 point cloud를 ASCII PLY로 저장한다."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {len(cloud.points_xyz)}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write("end_header\n")
        for x, y, z in cloud.points_xyz:
            file.write(f"{x:.6f} {y:.6f} {z:.6f}\n")


def oriented_bbox_corners(prior: ObjectPrior) -> np.ndarray:
    """`ObjectPrior`의 oriented bbox 8개 corner를 월드 좌표로 계산한다."""
    half = prior.dimensions_m / 2.0
    local_corners = np.array(
        [
            [x, y, z]
            for x in (-half[0], half[0])
            for y in (-half[1], half[1])
            for z in (-half[2], half[2])
        ],
        dtype=np.float32,
    )
    return prior.center_xyz + local_corners @ prior.axes.T


def export_oriented_bbox_ply(prior: ObjectPrior, output_path: Path) -> None:
    """oriented bbox를 edge가 포함된 ASCII PLY로 저장한다."""
    corners = oriented_bbox_corners(prior)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {len(corners)}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write(f"element edge {len(BBOX_EDGE_INDICES)}\n")
        file.write("property int vertex1\n")
        file.write("property int vertex2\n")
        file.write("end_header\n")
        for x, y, z in corners:
            file.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
        for start, end in BBOX_EDGE_INDICES:
            file.write(f"{start} {end}\n")


def export_scene_artifacts(
    cloud: PointCloudRecord,
    prior: ObjectPrior,
    output_dir: Path,
) -> dict[str, Any]:
    """point cloud, bbox, scene manifest를 한 번에 저장한다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    point_cloud_path = output_dir / f"{cloud.object_id}_cloud.ply"
    bbox_path = output_dir / f"{cloud.object_id}_bbox.ply"
    manifest_path = output_dir / "scene_manifest.json"

    export_point_cloud_ply(cloud, point_cloud_path)
    export_oriented_bbox_ply(prior, bbox_path)

    manifest: dict[str, Any] = {
        "object_id": prior.object_id,
        "bbox_type": "oriented",
        "center_xyz": prior.center_xyz.tolist(),
        "axes": prior.axes.tolist(),
        "dimensions_m": prior.dimensions_m.tolist(),
        "confidence": prior.confidence,
        "source_frame_ids": list(cloud.source_frame_ids),
        "assets": {
            "point_cloud_ply": str(point_cloud_path),
            "bbox_ply": str(bbox_path),
            "scene_manifest_json": str(manifest_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
