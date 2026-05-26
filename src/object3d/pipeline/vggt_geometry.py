"""이미지 한 장 이상을 VGGT geometry `.npz` 산출물로 변환하는 CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_vggt_geometry import run_vggt_geometry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.vggt_geometry",
        description="Run VGGT geometry inference and save geometry.npz.",
    )
    parser.add_argument(
        "--image-path",
        type=Path,
        action="append",
        required=True,
        help="Input image path. Repeat this option for multi-view smoke.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Path where geometry.npz will be written.",
    )
    parser.add_argument("--frame-index", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--model-id", default="facebook/VGGT-1B")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_vggt_geometry(
        image_paths=args.image_path,
        output_path=args.output_path,
        frame_index=args.frame_index,
        device=args.device,
        model_id=args.model_id,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
