"""mock MVP 파이프라인을 실행하는 작은 CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_mock_mvp import run_mock_mvp


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 parser를 만든다."""
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline",
        description="Run the mock No-Training MVP pipeline.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where summary.json and point cloud files will be written.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """mock MVP를 실행하고 summary JSON을 파일과 stdout에 남긴다."""
    args = build_parser().parse_args(argv)
    summary = run_mock_mvp(args.output_dir)
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0
