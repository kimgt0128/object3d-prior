"""대표 synthetic smoke fixture를 생성하는 CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.validation.smoke_fixtures import materialize_smoke_fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.generate_smoke_fixtures",
        description="Generate representative synthetic smoke fixtures.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = materialize_smoke_fixtures(args.output_dir)
    summary = {
        "case_count": len(manifest["cases"]),
        "cases": manifest["cases"],
        "manifest_json": manifest["manifest_json"],
        "source": manifest["source"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
