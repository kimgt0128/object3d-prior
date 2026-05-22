from pathlib import Path

from object3d.pipeline.run_mock_mvp import run_mock_mvp


def test_run_mock_mvp_exports_cloud_and_metrics(tmp_path: Path) -> None:
    result = run_mock_mvp(output_dir=tmp_path)

    assert result["object_id"] == "object_001"
    assert Path(result["point_cloud_ply"]).exists()
    assert len(result["dimensions_m"]) == 3
    assert "absolute_error_m" in result["dimension_errors"]
    assert result["source_frame_ids"] == [0, 1]
