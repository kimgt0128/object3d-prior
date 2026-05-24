import json
from pathlib import Path

from object3d.pipeline.generate_smoke_fixtures import main


def test_generate_smoke_fixtures_cli_writes_manifest(tmp_path: Path, capsys) -> None:
    output_dir = tmp_path / "fixtures"

    exit_code = main(["--output-dir", str(output_dir)])

    assert exit_code == 0
    stdout = json.loads(capsys.readouterr().out)
    manifest_path = Path(stdout["manifest_json"])
    assert manifest_path.exists()
    assert stdout["case_count"] == 3
    assert [case["case_id"] for case in stdout["cases"]] == [
        "laptop",
        "receipt",
        "tablet_keyboard",
    ]
