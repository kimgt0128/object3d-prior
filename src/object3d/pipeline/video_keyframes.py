"""Extract keyframes from a video into a frame manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.capture.frame_source import VideoFrameSource
from object3d.pipeline.run_video_keyframes import run_video_keyframes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.video_keyframes",
        description="Extract sampled keyframes from a video.",
    )
    parser.add_argument(
        "--video-path",
        type=Path,
        required=True,
        help="Input video path. Keep original videos out of git.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where keyframe PNG files will be written.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        required=True,
        help="Output frame manifest JSON path.",
    )
    parser.add_argument(
        "--target-fps",
        type=float,
        default=0.5,
        help="Sampling rate in frames per second.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = VideoFrameSource(str(args.video_path))
    summary = run_video_keyframes(
        source=source,
        source_video=str(args.video_path),
        output_dir=args.output_dir,
        manifest_path=args.manifest_path,
        target_fps=args.target_fps,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
