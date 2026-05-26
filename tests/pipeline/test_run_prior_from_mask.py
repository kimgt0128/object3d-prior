import json
from pathlib import Path

import numpy as np

from object3d.pipeline.prior_from_mask import main
from object3d.pipeline.run_prior_from_mask import run_prior_from_mask


def _write_segmentation_summary(tmp_path: Path) -> Path:
    mask = np.zeros((10, 12), dtype=bool)
    mask[3:7, 2:9] = True
    mask_path = tmp_path / "mask.npy"
    summary_path = tmp_path / "summary.json"
    np.save(mask_path, mask)
    summary = {
        "backend": "manual",
        "object_id": "object_001",
        "frame_id": 0,
        "image_path": str(tmp_path / "frame.png"),
        "confidence": 0.75,
        "mask_shape": [10, 12],
        "mask_pixels": int(mask.sum()),
        "mask_npy": str(mask_path),
        "summary_json": str(summary_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary_path


def test_run_prior_from_mask_creates_3d_scene_artifacts(tmp_path: Path) -> None:
    segmentation_summary = _write_segmentation_summary(tmp_path)
    output_dir = tmp_path / "prior"

    summary = run_prior_from_mask(
        segmentation_summary_path=segmentation_summary,
        output_dir=output_dir,
        depth_m=2.0,
    )

    assert summary["object_id"] == "object_001"
    assert summary["source"] == "segmentation_summary"
    assert summary["depth_m"] == 2.0
    assert summary["mask_pixels"] == 28
    assert summary["point_count"] == 28
    assert summary["bbox_type"] == "oriented"
    assert len(summary["dimensions_m"]) == 3
    assert Path(summary["point_cloud_ply"]).exists()
    assert Path(summary["bbox_ply"]).exists()
    assert Path(summary["scene_manifest_json"]).exists()
    assert Path(summary["summary_json"]).exists()


def test_prior_from_mask_cli_outputs_summary(tmp_path: Path, capsys) -> None:
    segmentation_summary = _write_segmentation_summary(tmp_path)
    output_dir = tmp_path / "prior"

    exit_code = main(
        [
            "--segmentation-summary",
            str(segmentation_summary),
            "--output-dir",
            str(output_dir),
            "--depth-m",
            "2.5",
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["depth_m"] == 2.5
    assert stdout["point_count"] == 28
    assert Path(stdout["scene_manifest_json"]).exists()


def test_prior_from_mask_cli_accepts_geometry_npz(tmp_path: Path, capsys) -> None:
    segmentation_summary = _write_segmentation_summary(tmp_path)
    geometry_npz = tmp_path / "geometry.npz"
    output_dir = tmp_path / "prior"
    np.savez(
        geometry_npz,
        depth_m=np.full((10, 12), 3.0, dtype=np.float32),
        intrinsics=np.array(
            [[120.0, 0.0, 6.0], [0.0, 120.0, 5.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ),
        camera_to_world=np.eye(4, dtype=np.float32),
    )

    exit_code = main(
        [
            "--segmentation-summary",
            str(segmentation_summary),
            "--output-dir",
            str(output_dir),
            "--geometry-npz",
            str(geometry_npz),
        ]
    )

    stdout = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert stdout["geometry_source"] == "npz"
    assert stdout["geometry_npz"] == str(geometry_npz)
    assert stdout["center_xyz"][2] == 3.0
    assert stdout["point_count"] == 28
    assert Path(stdout["scene_manifest_json"]).exists()


def test_run_prior_from_mask_resizes_mask_to_geometry_shape_for_vggt_depth(
    tmp_path: Path,
) -> None:
    segmentation_summary = _write_segmentation_summary(tmp_path)
    geometry_npz = tmp_path / "geometry.npz"
    output_dir = tmp_path / "prior"
    np.savez(
        geometry_npz,
        depth_m=np.full((5, 6), 3.0, dtype=np.float32),
        intrinsics=np.array(
            [[60.0, 0.0, 3.0], [0.0, 60.0, 2.5], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ),
        camera_to_world=np.eye(4, dtype=np.float32),
    )

    summary = run_prior_from_mask(
        segmentation_summary_path=segmentation_summary,
        output_dir=output_dir,
        depth_m=2.0,
        geometry_npz_path=geometry_npz,
    )

    assert summary["mask_alignment"] == "resized_to_geometry"
    assert summary["input_mask_shape"] == [10, 12]
    assert summary["geometry_depth_shape"] == [5, 6]
    assert summary["effective_mask_shape"] == [5, 6]
    assert summary["point_count"] == summary["mask_pixels"]
    assert Path(summary["mask_npy"]).exists()
    assert Path(summary["resized_mask_npy"]).exists()
