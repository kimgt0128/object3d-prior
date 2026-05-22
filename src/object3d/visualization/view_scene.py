"""Scene manifest를 summary 또는 optional viewer backend로 여는 도구."""

from __future__ import annotations

import json
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Sequence

import numpy as np
from numpy.typing import NDArray


class OptionalViewerDependencyError(ImportError):
    """선택 viewer dependency가 없을 때 발생하는 에러."""


@dataclass(frozen=True)
class PlyData:
    """viewer backend가 소비할 최소 ASCII PLY 데이터."""

    vertices: NDArray[np.float32]
    edges: list[tuple[int, int]]


def load_scene_summary(manifest_path: Path) -> dict[str, Any]:
    """scene manifest를 읽고 asset 존재 여부를 함께 반환한다."""
    manifest = _load_manifest(manifest_path)
    assets = manifest.get("assets", {})
    resolved_assets = {
        key: str(_resolve_asset_path(manifest_path, value))
        for key, value in assets.items()
    }
    asset_exists = {
        key: Path(value).exists()
        for key, value in resolved_assets.items()
    }

    summary = dict(manifest)
    summary["assets"] = resolved_assets
    summary["asset_exists"] = asset_exists
    return summary


def read_ascii_ply(path: Path) -> PlyData:
    """이 프로젝트에서 생성한 ASCII PLY의 vertex와 edge를 읽는다."""
    lines = path.read_text(encoding="utf-8").splitlines()
    vertex_count = 0
    edge_count = 0
    data_start = 0
    for index, line in enumerate(lines):
        if line.startswith("element vertex "):
            vertex_count = int(line.split()[-1])
        elif line.startswith("element edge "):
            edge_count = int(line.split()[-1])
        elif line == "end_header":
            data_start = index + 1
            break

    vertex_lines = lines[data_start : data_start + vertex_count]
    edge_lines = lines[data_start + vertex_count : data_start + vertex_count + edge_count]
    vertices = np.array(
        [[float(value) for value in line.split()[:3]] for line in vertex_lines],
        dtype=np.float32,
    )
    edges = [
        (int(parts[0]), int(parts[1]))
        for parts in (line.split() for line in edge_lines)
    ]
    return PlyData(vertices=vertices, edges=edges)


def view_scene(
    manifest_path: Path,
    *,
    backend: Literal["summary", "rerun"] = "summary",
    app_id: str = "object3d-prior",
    spawn: bool = False,
) -> dict[str, Any]:
    """scene manifest를 선택 backend로 연다."""
    summary = load_scene_summary(manifest_path)
    if backend == "summary":
        summary["backend"] = "summary"
        return summary
    if backend == "rerun":
        _log_rerun_scene(summary, app_id=app_id, spawn=spawn)
        summary["backend"] = "rerun"
        return summary
    raise ValueError("backend must be 'summary' or 'rerun'")


def build_parser() -> argparse.ArgumentParser:
    """scene viewer CLI parser를 만든다."""
    parser = argparse.ArgumentParser(
        prog="python -m object3d.visualization.view_scene",
        description="View or summarize an Object3D scene manifest.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to scene_manifest.json.",
    )
    parser.add_argument(
        "--backend",
        choices=("summary", "rerun"),
        default="summary",
        help="Viewer backend. rerun requires optional rerun-sdk dependency.",
    )
    parser.add_argument(
        "--app-id",
        default="object3d-prior",
        help="Rerun application id.",
    )
    parser.add_argument(
        "--spawn",
        action="store_true",
        help="Ask Rerun to spawn a viewer process.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """scene manifest를 열고 summary JSON을 stdout에 출력한다."""
    args = build_parser().parse_args(argv)
    summary = view_scene(
        args.manifest,
        backend=args.backend,
        app_id=args.app_id,
        spawn=args.spawn,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def _log_rerun_scene(summary: dict[str, Any], *, app_id: str, spawn: bool) -> None:
    try:
        import rerun as rr
    except ImportError as error:
        raise OptionalViewerDependencyError(
            "rerun is required for backend='rerun'. "
            "Install rerun-sdk before using the rerun viewer backend."
        ) from error

    object_id = summary["object_id"]
    assets = summary["assets"]
    point_cloud = read_ascii_ply(Path(assets["point_cloud_ply"]))
    bbox = read_ascii_ply(Path(assets["bbox_ply"]))
    bbox_strips = [
        bbox.vertices[[start, end]]
        for start, end in bbox.edges
    ]

    rr.init(app_id, spawn=spawn)
    rr.log(f"{object_id}/points", rr.Points3D(point_cloud.vertices))
    rr.log(f"{object_id}/bbox", rr.LineStrips3D(bbox_strips))


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _resolve_asset_path(manifest_path: Path, asset_path: str) -> Path:
    path = Path(asset_path)
    if path.is_absolute() or path.exists():
        return path
    return manifest_path.parent / path


if __name__ == "__main__":
    raise SystemExit(main())
