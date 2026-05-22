# No-Training MVP Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 빈 `src/`에서 시작해 단일 객체 3D object prior를 mock 기반으로 end-to-end 실행할 수 있는 No-Training MVP 코드 뼈대를 만든다.

**Architecture:** 먼저 `object3d` Python package와 dataclass contract를 만든다. 이후 capture, segmentation mock, geometry mock, masked back-projection, point-cloud fusion, bbox fitting, evaluation, visualization export를 독립 모듈로 쌓고, 마지막에 CLI pipeline으로 연결한다. 실제 SAM/SAM2, MapAnything, VGGT 연동은 contract가 안정된 뒤 별도 adapter 작업으로 분리한다.

**Tech Stack:** Python 3.11+, `numpy`, `opencv-python`, `pytest`, optional `open3d`/`rerun` later. 첫 MVP는 `numpy`와 `opencv-python` 중심으로 구현한다.

---

## Current State

- `src/`에는 `src/README.md`만 있고 실제 Python package는 없다.
- 테스트 폴더와 `pyproject.toml`이 없다.
- Serena 설정은 존재하지만 분석 가능한 Python source가 없어 `serena project health-check`가 `No analyzable files found`로 실패한다.
- 기존 `.claude/`, `project/`, `cv_tutorial/`, `reference/`는 이번 구현에서 수정하지 않는다.

## Implementation Boundaries

Create:

- `pyproject.toml`
- `src/object3d/__init__.py`
- `src/object3d/contracts.py`
- `src/object3d/capture/frame_sampler.py`
- `src/object3d/adapters/segmentation/mock.py`
- `src/object3d/adapters/geometry/mock.py`
- `src/object3d/geometry/backprojection.py`
- `src/object3d/reconstruction/fusion.py`
- `src/object3d/priors/bbox.py`
- `src/object3d/evaluation/metrics.py`
- `src/object3d/visualization/export.py`
- `src/object3d/pipeline/run_mock_mvp.py`
- matching tests under `tests/`

Do not create yet:

- real SAM/SAM2 adapter
- real MapAnything/VGGT/COLMAP adapter
- large dataset folder
- GPU training code
- dense room reconstruction code

## Git Preflight

Before implementation:

- [ ] **Step 1: Create or confirm GitHub Issue**

Use an issue title like:

```text
[Feat] No-Training MVP 소스 파이프라인 구축
```

Expected issue scope:

```text
mock 기반 frame -> mask -> depth/pose -> point cloud -> bbox -> evaluation/export 흐름 구현
```

- [ ] **Step 2: Create branch from the Issue**

Expected branch name:

```text
feat/<issue-number>-no-training-mvp-src
```

- [ ] **Step 3: Protect unrelated changes**

Run:

```bash
git status --short
```

Expected:

```text
현재 작업과 무관한 삭제/수정이 있으면 건드리지 않는다.
```

---

## Task 1: Package Foundation

**Files:**

- Create: `pyproject.toml`
- Create: `src/object3d/__init__.py`
- Create: `tests/test_package_import.py`

- [ ] **Step 1: Write import test**

Create `tests/test_package_import.py`:

```python
def test_object3d_package_imports() -> None:
    import object3d

    assert object3d.__version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_package_import.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'object3d'
```

- [ ] **Step 3: Add project package config**

Create `pyproject.toml`:

```toml
[project]
name = "object3d-prior"
version = "0.1.0"
description = "SAM mask based 3D object prior MVP"
requires-python = ">=3.11"
dependencies = [
  "numpy>=1.26",
  "opencv-python>=4.9",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Create `src/object3d/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_package_import.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/object3d/__init__.py tests/test_package_import.py
git commit -m "chore(#<issue>): Python 패키지 기본 구조 추가"
```

---

## Task 2: Shared Contracts

**Files:**

- Create: `src/object3d/contracts.py`
- Create: `tests/test_contracts.py`

- [ ] **Step 1: Write contract tests**

Create `tests/test_contracts.py`:

```python
import numpy as np

from object3d.contracts import FrameRecord, GeometryRecord, MaskRecord


def test_frame_record_keeps_frame_identity() -> None:
    frame = FrameRecord(
        frame_id="frame_000001",
        image_path="data/interim/frames/frame_000001.png",
        timestamp_sec=0.5,
        width=640,
        height=480,
    )

    assert frame.frame_id == "frame_000001"
    assert frame.width == 640
    assert frame.height == 480


def test_mask_record_validates_mask_shape() -> None:
    mask = np.ones((480, 640), dtype=bool)
    record = MaskRecord(
        frame_id="frame_000001",
        object_id="object_001",
        mask=mask,
        confidence=0.95,
    )

    assert record.mask.dtype == bool
    assert record.mask.shape == (480, 640)


def test_geometry_record_contains_camera_matrices() -> None:
    depth = np.ones((2, 3), dtype=np.float32)
    intrinsics = np.eye(3, dtype=np.float32)
    camera_to_world = np.eye(4, dtype=np.float32)

    record = GeometryRecord(
        frame_id="frame_000001",
        depth_m=depth,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )

    assert record.depth_m.shape == (2, 3)
    assert record.intrinsics.shape == (3, 3)
    assert record.camera_to_world.shape == (4, 4)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_contracts.py -q
```

Expected:

```text
ModuleNotFoundError or ImportError for object3d.contracts
```

- [ ] **Step 3: Implement contracts**

Create `src/object3d/contracts.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class FrameRecord:
    frame_id: str
    image_path: str
    timestamp_sec: float
    width: int
    height: int


@dataclass(frozen=True)
class MaskRecord:
    frame_id: str
    object_id: str
    mask: BoolArray
    confidence: float

    def __post_init__(self) -> None:
        if self.mask.ndim != 2:
            raise ValueError("mask must be a 2D boolean array")
        if self.mask.dtype != np.bool_:
            raise ValueError("mask dtype must be bool")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class GeometryRecord:
    frame_id: str
    depth_m: FloatArray
    intrinsics: FloatArray
    camera_to_world: FloatArray

    def __post_init__(self) -> None:
        if self.depth_m.ndim != 2:
            raise ValueError("depth_m must be a 2D array")
        if self.intrinsics.shape != (3, 3):
            raise ValueError("intrinsics must have shape (3, 3)")
        if self.camera_to_world.shape != (4, 4):
            raise ValueError("camera_to_world must have shape (4, 4)")


@dataclass(frozen=True)
class PointCloudRecord:
    object_id: str
    points_xyz: FloatArray
    source_frame_ids: tuple[str, ...]


@dataclass(frozen=True)
class ObjectPrior:
    object_id: str
    center_xyz: FloatArray
    axes: FloatArray
    dimensions_m: FloatArray
    confidence: float
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_contracts.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add src/object3d/contracts.py tests/test_contracts.py
git commit -m "feat(#<issue>): MVP 공통 데이터 계약 추가"
```

---

## Task 3: Capture Frame Sampling

**Files:**

- Create: `src/object3d/capture/__init__.py`
- Create: `src/object3d/capture/frame_sampler.py`
- Create: `tests/capture/test_frame_sampler.py`

- [ ] **Step 1: Write tests**

Create `tests/capture/test_frame_sampler.py`:

```python
from pathlib import Path

import cv2
import numpy as np

from object3d.capture.frame_sampler import sample_video_frames


def _write_test_video(path: Path) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10.0,
        (64, 48),
    )
    for index in range(10):
        frame = np.full((48, 64, 3), index * 20, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_sample_video_frames_writes_images_and_manifest(tmp_path: Path) -> None:
    video_path = tmp_path / "input.mp4"
    output_dir = tmp_path / "frames"
    _write_test_video(video_path)

    records = sample_video_frames(video_path, output_dir, every_n_frames=3)

    assert [record.frame_id for record in records] == [
        "frame_000000",
        "frame_000003",
        "frame_000006",
        "frame_000009",
    ]
    assert all(Path(record.image_path).exists() for record in records)
    assert records[0].width == 64
    assert records[0].height == 48
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/capture/test_frame_sampler.py -q
```

Expected:

```text
ImportError for object3d.capture.frame_sampler
```

- [ ] **Step 3: Implement frame sampler**

Create `src/object3d/capture/__init__.py`:

```python
"""Video capture and frame sampling utilities."""
```

Create `src/object3d/capture/frame_sampler.py`:

```python
from __future__ import annotations

from pathlib import Path

import cv2

from object3d.contracts import FrameRecord


def sample_video_frames(
    video_path: Path,
    output_dir: Path,
    *,
    every_n_frames: int,
) -> list[FrameRecord]:
    if every_n_frames <= 0:
        raise ValueError("every_n_frames must be positive")

    output_dir.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"failed to open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
    records: list[FrameRecord] = []
    frame_index = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        if frame_index % every_n_frames == 0:
            frame_id = f"frame_{frame_index:06d}"
            image_path = output_dir / f"{frame_id}.png"
            cv2.imwrite(str(image_path), frame)
            height, width = frame.shape[:2]
            timestamp_sec = frame_index / fps if fps > 0 else 0.0
            records.append(
                FrameRecord(
                    frame_id=frame_id,
                    image_path=str(image_path),
                    timestamp_sec=timestamp_sec,
                    width=width,
                    height=height,
                )
            )

        frame_index += 1

    capture.release()
    return records
```

- [ ] **Step 4: Run test**

```bash
pytest tests/capture/test_frame_sampler.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add src/object3d/capture tests/capture
git commit -m "feat(#<issue>): 입력 영상 프레임 샘플링 추가"
```

---

## Task 4: Mock Segmentation and Geometry Adapters

**Files:**

- Create: `src/object3d/adapters/__init__.py`
- Create: `src/object3d/adapters/segmentation/__init__.py`
- Create: `src/object3d/adapters/segmentation/mock.py`
- Create: `src/object3d/adapters/geometry/__init__.py`
- Create: `src/object3d/adapters/geometry/mock.py`
- Create: `tests/adapters/test_mock_adapters.py`

- [ ] **Step 1: Write tests**

Create `tests/adapters/test_mock_adapters.py`:

```python
import numpy as np

from object3d.adapters.geometry.mock import make_planar_mock_geometry
from object3d.adapters.segmentation.mock import make_center_box_mask
from object3d.contracts import FrameRecord


def test_make_center_box_mask_returns_bool_mask() -> None:
    frame = FrameRecord("frame_000000", "frame.png", 0.0, 100, 80)

    mask = make_center_box_mask(frame, object_id="object_001", box_fraction=0.5)

    assert mask.object_id == "object_001"
    assert mask.mask.dtype == np.bool_
    assert mask.mask.shape == (80, 100)
    assert mask.mask.sum() == 40 * 50


def test_make_planar_mock_geometry_shapes() -> None:
    frame = FrameRecord("frame_000000", "frame.png", 0.0, 100, 80)

    geometry = make_planar_mock_geometry(frame, depth_m=2.0)

    assert geometry.depth_m.shape == (80, 100)
    assert geometry.intrinsics.shape == (3, 3)
    assert geometry.camera_to_world.shape == (4, 4)
    assert float(geometry.depth_m[0, 0]) == 2.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/adapters/test_mock_adapters.py -q
```

Expected:

```text
ImportError for object3d.adapters
```

- [ ] **Step 3: Implement mock adapters**

Create package `__init__.py` files with docstrings:

```python
"""Model adapter package."""
```

Create `src/object3d/adapters/segmentation/mock.py`:

```python
from __future__ import annotations

import numpy as np

from object3d.contracts import FrameRecord, MaskRecord


def make_center_box_mask(
    frame: FrameRecord,
    *,
    object_id: str,
    box_fraction: float,
) -> MaskRecord:
    if not 0.0 < box_fraction <= 1.0:
        raise ValueError("box_fraction must be in (0, 1]")

    mask = np.zeros((frame.height, frame.width), dtype=bool)
    box_width = int(frame.width * box_fraction)
    box_height = int(frame.height * box_fraction)
    x0 = (frame.width - box_width) // 2
    y0 = (frame.height - box_height) // 2
    mask[y0 : y0 + box_height, x0 : x0 + box_width] = True
    return MaskRecord(
        frame_id=frame.frame_id,
        object_id=object_id,
        mask=mask,
        confidence=1.0,
    )
```

Create `src/object3d/adapters/geometry/mock.py`:

```python
from __future__ import annotations

import numpy as np

from object3d.contracts import FrameRecord, GeometryRecord


def make_planar_mock_geometry(
    frame: FrameRecord,
    *,
    depth_m: float,
) -> GeometryRecord:
    if depth_m <= 0:
        raise ValueError("depth_m must be positive")

    depth = np.full((frame.height, frame.width), depth_m, dtype=np.float32)
    focal = float(max(frame.width, frame.height))
    intrinsics = np.array(
        [
            [focal, 0.0, frame.width / 2.0],
            [0.0, focal, frame.height / 2.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    return GeometryRecord(
        frame_id=frame.frame_id,
        depth_m=depth,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/adapters/test_mock_adapters.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add src/object3d/adapters tests/adapters
git commit -m "feat(#<issue>): mock segmentation과 geometry adapter 추가"
```

---

## Task 5: Masked Back-Projection

**Files:**

- Create: `src/object3d/geometry/__init__.py`
- Create: `src/object3d/geometry/backprojection.py`
- Create: `tests/geometry/test_backprojection.py`

- [ ] **Step 1: Write tests**

Create `tests/geometry/test_backprojection.py`:

```python
import numpy as np

from object3d.contracts import GeometryRecord, MaskRecord
from object3d.geometry.backprojection import backproject_masked_points


def test_backproject_masked_points_uses_intrinsics_and_depth() -> None:
    depth = np.ones((3, 3), dtype=np.float32) * 2.0
    intrinsics = np.array(
        [[2.0, 0.0, 1.0], [0.0, 2.0, 1.0], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    geometry = GeometryRecord("frame_000000", depth, intrinsics, camera_to_world)
    mask_array = np.zeros((3, 3), dtype=bool)
    mask_array[1, 1] = True
    mask = MaskRecord("frame_000000", "object_001", mask_array, 1.0)

    cloud = backproject_masked_points(mask, geometry)

    assert cloud.object_id == "object_001"
    assert cloud.source_frame_ids == ("frame_000000",)
    np.testing.assert_allclose(cloud.points_xyz, np.array([[0.0, 0.0, 2.0]], dtype=np.float32))
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/geometry/test_backprojection.py -q
```

Expected:

```text
ImportError for object3d.geometry.backprojection
```

- [ ] **Step 3: Implement back-projection**

Create `src/object3d/geometry/__init__.py`:

```python
"""Geometry utilities for 2D-to-3D projection."""
```

Create `src/object3d/geometry/backprojection.py`:

```python
from __future__ import annotations

import numpy as np

from object3d.contracts import GeometryRecord, MaskRecord, PointCloudRecord


def backproject_masked_points(
    mask: MaskRecord,
    geometry: GeometryRecord,
) -> PointCloudRecord:
    if mask.frame_id != geometry.frame_id:
        raise ValueError("mask and geometry must belong to the same frame")
    if mask.mask.shape != geometry.depth_m.shape:
        raise ValueError("mask and depth must have the same shape")

    v_coords, u_coords = np.nonzero(mask.mask)
    if len(u_coords) == 0:
        points = np.empty((0, 3), dtype=np.float32)
        return PointCloudRecord(mask.object_id, points, (mask.frame_id,))

    depth = geometry.depth_m[v_coords, u_coords].astype(np.float32)
    fx = geometry.intrinsics[0, 0]
    fy = geometry.intrinsics[1, 1]
    cx = geometry.intrinsics[0, 2]
    cy = geometry.intrinsics[1, 2]

    x = (u_coords.astype(np.float32) - cx) * depth / fx
    y = (v_coords.astype(np.float32) - cy) * depth / fy
    z = depth
    camera_points = np.stack([x, y, z, np.ones_like(z)], axis=1)
    world_points = (geometry.camera_to_world @ camera_points.T).T[:, :3]
    return PointCloudRecord(
        object_id=mask.object_id,
        points_xyz=world_points.astype(np.float32),
        source_frame_ids=(mask.frame_id,),
    )
```

- [ ] **Step 4: Run test**

```bash
pytest tests/geometry/test_backprojection.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

```bash
git add src/object3d/geometry tests/geometry
git commit -m "feat(#<issue>): 마스크 기반 3D 역투영 추가"
```

---

## Task 6: Point Cloud Fusion and Bbox Prior

**Files:**

- Create: `src/object3d/reconstruction/__init__.py`
- Create: `src/object3d/reconstruction/fusion.py`
- Create: `src/object3d/priors/__init__.py`
- Create: `src/object3d/priors/bbox.py`
- Create: `tests/reconstruction/test_fusion.py`
- Create: `tests/priors/test_bbox.py`

- [ ] **Step 1: Write fusion test**

Create `tests/reconstruction/test_fusion.py`:

```python
import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.reconstruction.fusion import fuse_point_clouds


def test_fuse_point_clouds_concatenates_points_and_sources() -> None:
    first = PointCloudRecord("object_001", np.array([[0.0, 0.0, 1.0]], dtype=np.float32), ("a",))
    second = PointCloudRecord("object_001", np.array([[1.0, 0.0, 1.0]], dtype=np.float32), ("b",))

    fused = fuse_point_clouds([first, second])

    assert fused.points_xyz.shape == (2, 3)
    assert fused.source_frame_ids == ("a", "b")
```

- [ ] **Step 2: Write bbox test**

Create `tests/priors/test_bbox.py`:

```python
import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.priors.bbox import fit_axis_aligned_bbox


def test_fit_axis_aligned_bbox_reports_dimensions() -> None:
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 3.0, 4.0],
            [1.0, 2.0, 3.0],
        ],
        dtype=np.float32,
    )
    cloud = PointCloudRecord("object_001", points, ("frame_000000",))

    prior = fit_axis_aligned_bbox(cloud)

    np.testing.assert_allclose(prior.center_xyz, np.array([1.0, 1.5, 2.0], dtype=np.float32))
    np.testing.assert_allclose(prior.dimensions_m, np.array([2.0, 3.0, 4.0], dtype=np.float32))
    assert prior.confidence == 1.0
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/reconstruction/test_fusion.py tests/priors/test_bbox.py -q
```

Expected:

```text
ImportError for reconstruction and priors modules
```

- [ ] **Step 4: Implement fusion**

Create `src/object3d/reconstruction/__init__.py`:

```python
"""Point cloud reconstruction utilities."""
```

Create `src/object3d/reconstruction/fusion.py`:

```python
from __future__ import annotations

import numpy as np

from object3d.contracts import PointCloudRecord


def fuse_point_clouds(clouds: list[PointCloudRecord]) -> PointCloudRecord:
    if not clouds:
        raise ValueError("clouds must not be empty")

    object_id = clouds[0].object_id
    if any(cloud.object_id != object_id for cloud in clouds):
        raise ValueError("all clouds must have the same object_id")

    points = np.concatenate([cloud.points_xyz for cloud in clouds], axis=0).astype(np.float32)
    frame_ids: list[str] = []
    for cloud in clouds:
        frame_ids.extend(cloud.source_frame_ids)
    return PointCloudRecord(object_id, points, tuple(frame_ids))
```

- [ ] **Step 5: Implement bbox prior**

Create `src/object3d/priors/__init__.py`:

```python
"""Object prior fitting utilities."""
```

Create `src/object3d/priors/bbox.py`:

```python
from __future__ import annotations

import numpy as np

from object3d.contracts import ObjectPrior, PointCloudRecord


def fit_axis_aligned_bbox(cloud: PointCloudRecord) -> ObjectPrior:
    if cloud.points_xyz.size == 0:
        raise ValueError("cannot fit bbox to an empty point cloud")

    mins = cloud.points_xyz.min(axis=0)
    maxs = cloud.points_xyz.max(axis=0)
    center = ((mins + maxs) / 2.0).astype(np.float32)
    dimensions = (maxs - mins).astype(np.float32)
    axes = np.eye(3, dtype=np.float32)
    return ObjectPrior(
        object_id=cloud.object_id,
        center_xyz=center,
        axes=axes,
        dimensions_m=dimensions,
        confidence=1.0,
    )
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/reconstruction/test_fusion.py tests/priors/test_bbox.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 7: Commit**

```bash
git add src/object3d/reconstruction src/object3d/priors tests/reconstruction tests/priors
git commit -m "feat(#<issue>): 객체 포인트 클라우드 fusion과 bbox prior 추가"
```

---

## Task 7: Evaluation and Visualization Export

**Files:**

- Create: `src/object3d/evaluation/__init__.py`
- Create: `src/object3d/evaluation/metrics.py`
- Create: `src/object3d/visualization/__init__.py`
- Create: `src/object3d/visualization/export.py`
- Create: `tests/evaluation/test_metrics.py`
- Create: `tests/visualization/test_export.py`

- [ ] **Step 1: Write metric test**

Create `tests/evaluation/test_metrics.py`:

```python
import numpy as np

from object3d.evaluation.metrics import dimension_errors


def test_dimension_errors_returns_absolute_and_relative_errors() -> None:
    predicted = np.array([2.0, 3.0, 4.0], dtype=np.float32)
    measured = np.array([1.0, 3.0, 2.0], dtype=np.float32)

    result = dimension_errors(predicted, measured)

    assert result["absolute_error_m"] == [1.0, 0.0, 2.0]
    assert result["relative_error_percent"] == [100.0, 0.0, 100.0]
```

- [ ] **Step 2: Write PLY export test**

Create `tests/visualization/test_export.py`:

```python
from pathlib import Path

import numpy as np

from object3d.contracts import PointCloudRecord
from object3d.visualization.export import export_point_cloud_ply


def test_export_point_cloud_ply_writes_ascii_ply(tmp_path: Path) -> None:
    cloud = PointCloudRecord(
        "object_001",
        np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]], dtype=np.float32),
        ("frame_000000",),
    )
    output_path = tmp_path / "cloud.ply"

    export_point_cloud_ply(cloud, output_path)

    text = output_path.read_text()
    assert "element vertex 2" in text
    assert "0.000000 1.000000 2.000000" in text
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/evaluation/test_metrics.py tests/visualization/test_export.py -q
```

Expected:

```text
ImportError for evaluation and visualization modules
```

- [ ] **Step 4: Implement metrics**

Create `src/object3d/evaluation/__init__.py`:

```python
"""Evaluation utilities."""
```

Create `src/object3d/evaluation/metrics.py`:

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def dimension_errors(
    predicted_m: NDArray[np.float32],
    measured_m: NDArray[np.float32],
) -> dict[str, list[float]]:
    if predicted_m.shape != measured_m.shape:
        raise ValueError("predicted_m and measured_m must have the same shape")
    if np.any(measured_m == 0):
        raise ValueError("measured dimensions must be non-zero")

    absolute = np.abs(predicted_m - measured_m)
    relative = absolute / np.abs(measured_m) * 100.0
    return {
        "absolute_error_m": [float(value) for value in absolute],
        "relative_error_percent": [float(value) for value in relative],
    }
```

- [ ] **Step 5: Implement PLY export**

Create `src/object3d/visualization/__init__.py`:

```python
"""Visualization and export utilities."""
```

Create `src/object3d/visualization/export.py`:

```python
from __future__ import annotations

from pathlib import Path

from object3d.contracts import PointCloudRecord


def export_point_cloud_ply(cloud: PointCloudRecord, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {len(cloud.points_xyz)}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write("end_header\n")
        for x, y, z in cloud.points_xyz:
            file.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/evaluation/test_metrics.py tests/visualization/test_export.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 7: Commit**

```bash
git add src/object3d/evaluation src/object3d/visualization tests/evaluation tests/visualization
git commit -m "feat(#<issue>): 측정 평가와 point cloud export 추가"
```

---

## Task 8: Mock End-to-End Pipeline

**Files:**

- Create: `src/object3d/pipeline/__init__.py`
- Create: `src/object3d/pipeline/run_mock_mvp.py`
- Create: `tests/pipeline/test_run_mock_mvp.py`

- [ ] **Step 1: Write pipeline test**

Create `tests/pipeline/test_run_mock_mvp.py`:

```python
from pathlib import Path

from object3d.pipeline.run_mock_mvp import run_mock_mvp


def test_run_mock_mvp_exports_cloud_and_metrics(tmp_path: Path) -> None:
    result = run_mock_mvp(output_dir=tmp_path)

    assert result["object_id"] == "object_001"
    assert Path(result["point_cloud_ply"]).exists()
    assert len(result["dimensions_m"]) == 3
    assert "absolute_error_m" in result["dimension_errors"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/pipeline/test_run_mock_mvp.py -q
```

Expected:

```text
ImportError for object3d.pipeline.run_mock_mvp
```

- [ ] **Step 3: Implement mock pipeline**

Create `src/object3d/pipeline/__init__.py`:

```python
"""End-to-end MVP pipelines."""
```

Create `src/object3d/pipeline/run_mock_mvp.py`:

```python
from __future__ import annotations

from pathlib import Path

import numpy as np

from object3d.adapters.geometry.mock import make_planar_mock_geometry
from object3d.adapters.segmentation.mock import make_center_box_mask
from object3d.contracts import FrameRecord
from object3d.evaluation.metrics import dimension_errors
from object3d.geometry.backprojection import backproject_masked_points
from object3d.priors.bbox import fit_axis_aligned_bbox
from object3d.reconstruction.fusion import fuse_point_clouds
from object3d.visualization.export import export_point_cloud_ply


def run_mock_mvp(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = [
        FrameRecord("frame_000000", "mock_frame_0.png", 0.0, 64, 48),
        FrameRecord("frame_000001", "mock_frame_1.png", 0.1, 64, 48),
    ]
    clouds = []
    for frame in frames:
        mask = make_center_box_mask(frame, object_id="object_001", box_fraction=0.5)
        geometry = make_planar_mock_geometry(frame, depth_m=2.0)
        clouds.append(backproject_masked_points(mask, geometry))

    fused = fuse_point_clouds(clouds)
    prior = fit_axis_aligned_bbox(fused)
    measured = np.array([0.5, 0.5, 0.01], dtype=np.float32)
    errors = dimension_errors(prior.dimensions_m, measured)
    ply_path = output_dir / "object_001_cloud.ply"
    export_point_cloud_ply(fused, ply_path)

    return {
        "object_id": prior.object_id,
        "center_xyz": prior.center_xyz.tolist(),
        "dimensions_m": prior.dimensions_m.tolist(),
        "confidence": prior.confidence,
        "dimension_errors": errors,
        "point_cloud_ply": str(ply_path),
    }
```

- [ ] **Step 4: Run pipeline test**

```bash
pytest tests/pipeline/test_run_mock_mvp.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Run full test suite**

```bash
pytest -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 6: Run Serena health-check**

```bash
serena project health-check
```

Expected:

```text
No analyzable files found 에러가 사라진다.
```

- [ ] **Step 7: Commit**

```bash
git add src/object3d/pipeline tests/pipeline
git commit -m "feat(#<issue>): mock 기반 end-to-end MVP 파이프라인 추가"
```

---

## Task 9: Documentation Update

**Files:**

- Modify: `src/README.md`

- [ ] **Step 1: Update `src/README.md`**

Add an "Implemented MVP modules" section:

```markdown
## 구현된 MVP 모듈

- `object3d.contracts`: frame, mask, geometry, point cloud, object prior 데이터 계약
- `object3d.capture`: 입력 영상 frame sampling
- `object3d.adapters.segmentation.mock`: SAM/SAM2 연동 전 mock mask adapter
- `object3d.adapters.geometry.mock`: 실 geometry 모델 연동 전 mock depth/pose adapter
- `object3d.geometry`: masked back-projection
- `object3d.reconstruction`: object point cloud fusion
- `object3d.priors`: bbox 기반 object prior fitting
- `object3d.evaluation`: 실측값 대비 dimension error 계산
- `object3d.visualization`: point cloud PLY export
- `object3d.pipeline`: mock 기반 end-to-end 실행 흐름

첫 MVP는 실제 SAM/SAM2와 MapAnything/VGGT를 바로 붙이지 않는다.
먼저 contract와 downstream geometry pipeline을 검증한 뒤 실제 adapter를 추가한다.
```

- [ ] **Step 2: Run doc sanity checks**

```bash
test -f src/README.md
python -m compileall src
pytest -q
```

Expected:

```text
compileall succeeds
all tests pass
```

- [ ] **Step 3: Commit**

```bash
git add src/README.md
git commit -m "docs(#<issue>): MVP 소스 구조 설명 추가"
```

---

## Self-Review Checklist

- [ ] Plan starts from current source reality: `src/README.md` only.
- [ ] Every task has exact file paths.
- [ ] Each code-bearing task includes concrete test and implementation snippets.
- [ ] Real SAM/SAM2 and MapAnything/VGGT are intentionally excluded from this first implementation.
- [ ] Serena health-check failure is accounted for and expected to resolve after Python files exist.
- [ ] Git flow follows Issue -> branch -> small commits -> PR.
- [ ] `project/`, `.claude/`, `reference/`, `cv_tutorial/` are not touched.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-22-no-training-mvp-src-plan.md`.

Two execution options:

1. **Subagent-Driven (recommended)** - dispatch a fresh worker per task, review between tasks, fast iteration.
2. **Inline Execution** - execute tasks in this session using `superpowers:executing-plans`, with checkpoints after each task.
