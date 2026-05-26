"""segmentation summary를 3D object prior로 변환하는 CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from object3d.pipeline.run_prior_from_mask import run_prior_from_mask


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m object3d.pipeline.prior_from_mask",
        description="Create a 3D object prior from a segmentation summary.",
    )
    parser.add_argument(
        "--segmentation-summary",
        type=Path,
        required=True,
        help="Path to segment_image summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where prior summary and scene assets will be written.",
    )
    parser.add_argument(
        "--depth-m",
        type=float,
        default=2.0,
        help="Temporary constant depth in meters for the mock geometry step.",
    )
    parser.add_argument(
        "--geometry-npz",
        type=Path,
        default=None,
        help="Optional .npz file containing depth_m, intrinsics, and camera_to_world.",
    )
    parser.add_argument(
        "--outlier-filter",
        choices=("none", "radial_percentile"),
        default="none",
        help="Optional point cloud outlier filter before bbox fitting.",
    )
    parser.add_argument(
        "--outlier-keep-ratio",
        type=float,
        default=0.95,
        help="Fraction of points to keep for radial_percentile filtering.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_prior_from_mask(
        segmentation_summary_path=args.segmentation_summary,
        output_dir=args.output_dir,
        depth_m=args.depth_m,
        geometry_npz_path=args.geometry_npz,
        outlier_filter=args.outlier_filter,
        outlier_keep_ratio=args.outlier_keep_ratio,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
