"""Run VGGT geometry on a sampled keyframe manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_vggt_geometry_batch import run_vggt_geometry_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.vggt_geometry_batch",
        description="Save one geometry.npz per keyframe from a VGGT batch prediction.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Frame manifest JSON produced by video_keyframes.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where frame geometry artifacts will be written.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device for VGGT inference, such as cpu, mps, or cuda.",
    )
    parser.add_argument(
        "--model-id",
        default="facebook/VGGT-1B",
        help="VGGT Hugging Face model id.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=12,
        help="Maximum keyframes to send to VGGT in one batch.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_vggt_geometry_batch(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        device=args.device,
        model_id=args.model_id,
        max_frames=args.max_frames,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
