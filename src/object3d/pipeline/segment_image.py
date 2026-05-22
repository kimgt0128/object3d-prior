"""이미지 한 장과 수동 prompt JSON을 segmentation 산출물로 변환하는 CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_manual_segmentation import run_manual_segmentation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.segment_image",
        description="Run manual-prompt segmentation on one image.",
    )
    parser.add_argument("--image-path", type=Path, required=True)
    parser.add_argument("--prompt-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--object-id", default="object_001")
    parser.add_argument("--frame-id", type=int, default=0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_manual_segmentation(
        image_path=args.image_path,
        prompt_json_path=args.prompt_json,
        output_dir=args.output_dir,
        object_id=args.object_id,
        frame_id=args.frame_id,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
