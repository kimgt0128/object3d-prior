"""실모델 연동 전 downstream 전체 흐름을 검증하는 mock MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from object3d.adapters.geometry.mock import make_planar_mock_geometry
from object3d.adapters.segmentation.mock import make_center_box_mask
from object3d.capture.records import FrameRecord
from object3d.evaluation.metrics import dimension_errors
from object3d.geometry.backprojection import backproject_masked_points
from object3d.priors.bbox import fit_axis_aligned_bbox
from object3d.reconstruction.fusion import fuse_point_clouds
from object3d.visualization.export import export_point_cloud_ply


def run_mock_mvp(output_dir: Path) -> dict[str, Any]:
    """mock frame 두 개로 object prior와 PLY export까지 실행한다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = [
        FrameRecord(frame_id=0, image_path="mock_frame_0.png", timestamp_s=0.0),
        FrameRecord(frame_id=1, image_path="mock_frame_1.png", timestamp_s=0.1),
    ]

    clouds = []
    for frame in frames:
        mask = make_center_box_mask(
            frame,
            image_shape=(48, 64),
            object_id="object_001",
            box_fraction=0.5,
        )
        geometry = make_planar_mock_geometry(
            frame,
            image_shape=(48, 64),
            depth_m=2.0,
        )
        clouds.append(backproject_masked_points(mask, geometry))

    fused = fuse_point_clouds(clouds)
    prior = fit_axis_aligned_bbox(fused)
    measured = np.array([1.0, 1.0, 0.01], dtype=np.float32)
    errors = dimension_errors(prior.dimensions_m, measured)
    ply_path = output_dir / "object_001_cloud.ply"
    export_point_cloud_ply(fused, ply_path)

    return {
        "object_id": prior.object_id,
        "center_xyz": prior.center_xyz.tolist(),
        "axes": prior.axes.tolist(),
        "dimensions_m": prior.dimensions_m.tolist(),
        "confidence": prior.confidence,
        "dimension_errors": errors,
        "point_cloud_ply": str(ply_path),
        "source_frame_ids": list(fused.source_frame_ids),
    }
