"""Run segmentation prompts across sampled keyframes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_segment_keyframes import run_segment_keyframes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.segment_keyframes",
        description="Run object prompt segmentation across a keyframe manifest.",
    )
    parser.add_argument(
        "--frame-manifest",
        type=Path,
        required=True,
        help="Frame manifest JSON produced by video_keyframes.",
    )
    parser.add_argument(
        "--prompt-manifest",
        type=Path,
        required=True,
        help="Object prompt manifest JSON listing object/frame prompts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where per-object segmentation artifacts will be written.",
    )
    parser.add_argument(
        "--backend",
        choices=("manual", "sam2"),
        default="manual",
        help="Segmentation backend. 'sam2' requires checkpoint/config paths.",
    )
    parser.add_argument("--checkpoint-path", type=Path)
    parser.add_argument("--config-path", type=Path)
    parser.add_argument("--device", default="cpu")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_segment_keyframes(
        frame_manifest_path=args.frame_manifest,
        prompt_manifest_path=args.prompt_manifest,
        output_dir=args.output_dir,
        backend=args.backend,
        checkpoint_path=args.checkpoint_path,
        config_path=args.config_path,
        device=args.device,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
