"""Fuse per-frame object prior summaries into one object prior."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_fuse_object_priors import run_fuse_object_priors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.fuse_object_priors",
        description="Fuse per-frame object prior summaries for one object.",
    )
    parser.add_argument(
        "--prior-summary",
        type=Path,
        action="append",
        required=True,
        help="Per-frame prior summary JSON. Repeat for multiple keyframes.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where fused cloud, bbox, scene manifest, and summary are written.",
    )
    parser.add_argument(
        "--outlier-filter",
        choices=("none", "radial_percentile"),
        default="none",
        help="Optional fused point cloud outlier filter.",
    )
    parser.add_argument(
        "--outlier-keep-ratio",
        type=float,
        default=0.95,
        help="Keep ratio for radial_percentile outlier filtering.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_fuse_object_priors(
        prior_summary_paths=args.prior_summary,
        output_dir=args.output_dir,
        outlier_filter=args.outlier_filter,
        outlier_keep_ratio=args.outlier_keep_ratio,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
