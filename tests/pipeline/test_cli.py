import json
from pathlib import Path

from object3d.pipeline.cli import main


def test_cli_writes_summary_json_and_returns_success(tmp_path: Path, capsys) -> None:
    exit_code = main(["--output-dir", str(tmp_path)])

    assert exit_code == 0
    summary_path = tmp_path / "summary.json"
    assert summary_path.exists()
    assert (tmp_path / "object_001_cloud.ply").exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["object_id"] == "object_001"
    assert summary["point_cloud_ply"] == str(tmp_path / "object_001_cloud.ply")

    stdout = json.loads(capsys.readouterr().out)
    assert stdout == summary
