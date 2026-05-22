"""Open3D/Rerun 연동 전 사용할 수 있는 경량 export 함수."""

from __future__ import annotations

from pathlib import Path

from object3d.contracts import PointCloudRecord


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
