# Room Object 3D Prior Final Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 2-week computer vision final project demo (#58) that reconstructs a coarse small-room 3D point cloud, estimates rough room/table planes, and lifts selected objects into 3D object priors with SAM2 + VGGT.

**Architecture:** Keep the project as a no-training pipeline. Extract keyframes from a slow room video, run VGGT once per keyframe batch to produce per-frame geometry, run SAM2/manual prompts for target objects, back-project object masks into world-space point clouds, fuse same-object clouds across frames, fit oriented bboxes, and document coarse room/plane/object results. The output is an analysis-grade demo, not a complete textured room mesh.

**Tech Stack:** Python, NumPy, OpenCV, SAM2 image predictor, VGGT geometry adapter, existing `GeometryRecord` / `MaskRecord` / `PointCloudRecord`, ASCII PLY exports, Rerun summaries, pytest.

---

## Project Scope

### In Scope

- Small static room or desk-area video, captured slowly for 30-60 seconds.
- Keyframe extraction from video into a reproducible manifest.
- Coarse room point cloud from VGGT depth/pose.
- Rough dominant plane estimation for floor/wall/table candidates.
- Object-level 3D priors for 2-3 objects, such as laptop, desk/table, chair, cup, box, or bed-side furniture.
- Cleanup comparison: raw object prior vs mask cleanup + point cloud filtering.
- Measurement comparison for at least 2 objects using manually measured dimensions.
- Final validation document with images, tables, failure analysis, and commands.

### Out of Scope

- Full textured mesh reconstruction of the whole room.
- Large-scale 3D scene completion.
- New model training or fine-tuning.
- Transparent/thin object specialist model.
- Automatic natural-language object discovery.
- Committing original room videos, private photos, checkpoints, `outputs/`, `.npz`, `.npy`, `.ply`, or `.rrd` artifacts.

## Current Implementation Snapshot

- `src/object3d/capture/` already supports `VideoFrameSource`, rational frame sampling, image export, and frame manifest writing.
- `src/object3d/pipeline/run_vggt_geometry.py` can run VGGT with one or more images and save one frame's `geometry.npz`.
- `src/object3d/pipeline/run_manual_segmentation.py` can run manual or SAM2 image segmentation for a single image/prompt.
- `src/object3d/pipeline/run_prior_from_mask.py` can align mask/depth shape, clean masks, back-project masked points, filter outliers, fit bbox, and export scene artifacts.
- `src/object3d/reconstruction/fusion.py` can concatenate point clouds but does not yet load prior summaries or apply post-fusion cleanup.
- `src/object3d/evaluation/metrics.py` can compare predicted and measured dimensions.

## File Map

- Create `src/object3d/pipeline/video_keyframes.py`
  - CLI entrypoint for video-to-keyframe manifest extraction.
- Create `src/object3d/pipeline/run_video_keyframes.py`
  - Library function wrapping `VideoFrameSource` and `run_capture`.
- Create `tests/pipeline/test_run_video_keyframes.py`
  - Unit tests using `ArrayFrameSource` and fake frames.
- Create `src/object3d/pipeline/vggt_geometry_batch.py`
  - CLI entrypoint for manifest-to-per-frame geometry artifacts.
- Create `src/object3d/pipeline/run_vggt_geometry_batch.py`
  - Calls VGGT once on selected keyframes and saves one `geometry.npz` per frame.
- Create `tests/pipeline/test_run_vggt_geometry_batch.py`
  - Injected fake VGGT runner tests.
- Create `src/object3d/pipeline/segment_keyframes.py`
  - CLI entrypoint for batch object segmentation across keyframes.
- Create `src/object3d/pipeline/run_segment_keyframes.py`
  - Reads an object prompt manifest and runs existing segmentation per frame/object.
- Create `tests/pipeline/test_run_segment_keyframes.py`
  - Manual predictor and fake prompt manifest tests.
- Create `src/object3d/pipeline/fuse_object_priors.py`
  - CLI entrypoint for fusing per-frame object priors.
- Create `src/object3d/pipeline/run_fuse_object_priors.py`
  - Loads prior summaries, reads object PLYs, fuses same-object world points, filters, fits final bbox.
- Create `tests/pipeline/test_run_fuse_object_priors.py`
  - Synthetic shifted cloud fusion and bbox tests.
- Create `src/object3d/reconstruction/plane.py`
  - NumPy plane fitting and dominant plane summary utilities.
- Create `src/object3d/pipeline/run_room_geometry_summary.py`
  - Samples VGGT depth into a coarse room point cloud and plane summaries.
- Create `src/object3d/pipeline/room_geometry_summary.py`
  - CLI entrypoint for room cloud and rough plane extraction.
- Create `tests/reconstruction/test_plane.py`
  - Plane fitting tests on synthetic floor/table/wall points.
- Create `tests/pipeline/test_run_room_geometry_summary.py`
  - Geometry `.npz` to room summary smoke test.
- Create `src/object3d/pipeline/evaluate_object_priors.py`
  - CLI entrypoint for measured dimension comparison.
- Create `src/object3d/pipeline/run_evaluate_object_priors.py`
  - Loads fused summaries and measured dimensions JSON.
- Create `tests/pipeline/test_run_evaluate_object_priors.py`
  - Dimension error and missing measurement tests.
- Create `docs/runbooks/20260527-room-video-capture-guide.md`
  - Capture guide for final project input video.
- Create `docs/validation/20260527-room-object-prior-final-smoke.md`
  - Final validation record for the selected room video.
- Modify `README.md`, `src/README.md`, and `docs/PLAN.md`
  - Reflect the final project direction and commands.

---

## T21: Video Keyframe Extraction

**Purpose:** Turn a 30-60 second room video into a small, reproducible set of frame images and a manifest.

**Files:**
- Create: `src/object3d/pipeline/run_video_keyframes.py`
- Create: `src/object3d/pipeline/video_keyframes.py`
- Test: `tests/pipeline/test_run_video_keyframes.py`
- Modify: `src/README.md`

- [x] **Step 1: Write failing tests for manifest extraction**

Add tests that prove:

```python
def test_run_video_keyframes_writes_manifest_with_sampled_frames(tmp_path):
    frames = [
        np.full((8, 8, 3), index, dtype=np.uint8)
        for index in range(12)
    ]
    source = ArrayFrameSource(frames, source_fps=6.0)

    summary = run_video_keyframes(
        source=source,
        source_video="synthetic://room",
        output_dir=tmp_path / "frames",
        manifest_path=tmp_path / "manifest.json",
        target_fps=2.0,
    )

    assert summary["frame_count"] == 4
    assert Path(summary["manifest_json"]).exists()
    assert all(Path(path).exists() for path in summary["frame_paths"])
```

- [x] **Step 2: Run the focused tests and verify RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_video_keyframes.py
```

Expected: fail because `object3d.pipeline.run_video_keyframes` does not exist.

- [x] **Step 3: Implement `run_video_keyframes`**

Implement a small wrapper around existing `run_capture`:

```python
def run_video_keyframes(
    *,
    source: FrameSource,
    source_video: str,
    output_dir: Path,
    manifest_path: Path,
    target_fps: float,
) -> dict[str, Any]:
    metadata = CaptureMetadata(
        source_video=source_video,
        source_fps=source.source_fps,
        target_fps=target_fps,
    )
    manifest = run_capture(
        source=source,
        metadata=metadata,
        target_fps=target_fps,
        output_dir=output_dir,
        manifest_path=manifest_path,
    )
    frame_paths = [
        str((manifest_path.parent / frame["image_path"]).resolve())
        for frame in manifest["frames"]
    ]
    return {
        "source": "video_keyframes",
        "source_video": source_video,
        "target_fps": float(target_fps),
        "frame_count": len(frame_paths),
        "frame_paths": frame_paths,
        "manifest_json": str(manifest_path),
    }
```

- [x] **Step 4: Add CLI**

`video_keyframes.py` should accept:

```text
--video-path
--output-dir
--manifest-path
--target-fps
```

The CLI constructs `VideoFrameSource(args.video_path)` and prints JSON summary.

- [x] **Step 5: Run tests and commit**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_video_keyframes.py tests/capture
```

Commit:

```bash
git add src/object3d/pipeline/run_video_keyframes.py src/object3d/pipeline/video_keyframes.py tests/pipeline/test_run_video_keyframes.py src/README.md
git commit -m "feat(#T21): 방 영상 keyframe 추출 CLI 추가" \
  -m "src/object3d/pipeline/run_video_keyframes.py: 기존 capture pipeline을 영상 keyframe smoke용 summary로 감쌉니다." \
  -m "src/object3d/pipeline/video_keyframes.py: video path를 받아 frame manifest를 만드는 CLI를 추가합니다." \
  -m "tests/pipeline/test_run_video_keyframes.py: synthetic frame source 기반 keyframe manifest 생성을 검증합니다."
```

---

## T22: VGGT Batch Geometry From Keyframes

**Purpose:** Run VGGT on selected keyframes once and save per-frame `geometry.npz` artifacts that share a multi-view prediction context.

**Files:**
- Create: `src/object3d/pipeline/run_vggt_geometry_batch.py`
- Create: `src/object3d/pipeline/vggt_geometry_batch.py`
- Test: `tests/pipeline/test_run_vggt_geometry_batch.py`
- Modify: `src/README.md`

- [x] **Step 1: Write failing fake-runner tests**

Test shape:

```python
def test_run_vggt_geometry_batch_writes_one_geometry_per_frame(tmp_path):
    manifest_path = _write_manifest_with_three_images(tmp_path)

    def fake_runner(*, image_paths, device, model_id):
        return {
            "depth_map": np.ones((3, 4, 5, 1), dtype=np.float32),
            "intrinsic": np.repeat(np.eye(3, dtype=np.float32)[None], 3, axis=0),
            "extrinsic": np.repeat(np.eye(3, 4, dtype=np.float32)[None], 3, axis=0),
        }

    summary = run_vggt_geometry_batch(
        manifest_path=manifest_path,
        output_dir=tmp_path / "geometry",
        device="cpu",
        runner=fake_runner,
    )

    assert summary["geometry_count"] == 3
    assert [item["frame_id"] for item in summary["geometries"]] == [0, 1, 2]
    assert all(Path(item["geometry_npz"]).exists() for item in summary["geometries"])
```

- [x] **Step 2: Run RED**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_vggt_geometry_batch.py
```

Expected: fail because batch module does not exist.

- [x] **Step 3: Implement batch save**

Use existing `run_vggt_geometry` runner contract and `save_vggt_geometry_npz`:

```python
prediction = prediction_runner(
    image_paths=tuple(image_paths),
    device=device,
    model_id=model_id,
)
for frame_index, frame in enumerate(frames):
    output_path = output_dir / f"frame_{frame['frame_id']:06d}" / "geometry.npz"
    geometry_summary = save_vggt_geometry_npz(
        prediction,
        output_path=output_path,
        frame_index=frame_index,
    )
```

Record `frame_id`, `source_image_path`, `geometry_npz`, and `geometry_depth_shape` in `geometry_batch.summary.json`.

- [x] **Step 4: Add CLI**

`vggt_geometry_batch.py` should accept:

```text
--manifest
--output-dir
--device
--model-id
--max-frames
```

Default `--max-frames` should be conservative: `12` on local Mac; allow school GPU to raise it.

- [x] **Step 5: Run tests and commit**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_vggt_geometry.py tests/pipeline/test_run_vggt_geometry_batch.py tests/adapters/test_vggt_geometry.py
```

Commit:

```bash
git add src/object3d/pipeline/run_vggt_geometry_batch.py src/object3d/pipeline/vggt_geometry_batch.py tests/pipeline/test_run_vggt_geometry_batch.py src/README.md
git commit -m "feat(#T22): keyframe VGGT batch geometry 저장 추가" \
  -m "src/object3d/pipeline/run_vggt_geometry_batch.py: manifest 이미지를 VGGT에 한 번 넣고 frame별 geometry.npz를 저장합니다." \
  -m "src/object3d/pipeline/vggt_geometry_batch.py: batch geometry CLI를 추가합니다." \
  -m "tests/pipeline/test_run_vggt_geometry_batch.py: injected fake runner로 checkpoint 없이 batch 저장을 검증합니다."
```

---

## T23: Batch Segmentation For Selected Objects

**Purpose:** Segment 2-3 target objects across keyframes with a reproducible prompt manifest.

**Files:**
- Create: `src/object3d/pipeline/run_segment_keyframes.py`
- Create: `src/object3d/pipeline/segment_keyframes.py`
- Test: `tests/pipeline/test_run_segment_keyframes.py`
- Create: `docs/runbooks/20260527-room-video-capture-guide.md`

- [ ] **Step 1: Define object prompt manifest**

Use a JSON format that is easy to hand-author:

```json
{
  "objects": [
    {
      "object_id": "laptop_001",
      "frames": [
        {
          "frame_id": 0,
          "prompt_json": "outputs/room/prompts/laptop_frame_000000.json"
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Write failing batch segmentation test**

```python
def test_run_segment_keyframes_runs_manual_prompts_for_each_object_frame(tmp_path):
    manifest_path = _write_frame_manifest(tmp_path)
    prompt_manifest_path = _write_prompt_manifest(tmp_path)

    summary = run_segment_keyframes(
        frame_manifest_path=manifest_path,
        prompt_manifest_path=prompt_manifest_path,
        output_dir=tmp_path / "segmentation",
        backend="manual",
    )

    assert summary["object_count"] == 1
    assert summary["segmentation_count"] == 2
    assert Path(summary["objects"][0]["frames"][0]["summary_json"]).exists()
```

- [ ] **Step 3: Implement the runner**

For each object/frame pair:

```python
segmentation_summary = run_manual_segmentation(
    image_path=image_path,
    prompt_json_path=prompt_path,
    output_dir=object_output_dir / f"frame_{frame_id:06d}",
    object_id=object_id,
    frame_id=frame_id,
    backend=backend,
    checkpoint_path=checkpoint_path,
    config_path=config_path,
    device=device,
)
```

- [ ] **Step 4: Add CLI**

`segment_keyframes.py` should accept:

```text
--frame-manifest
--prompt-manifest
--output-dir
--backend manual|sam2
--checkpoint
--config
--device
```

- [ ] **Step 5: Add capture runbook**

Include these exact project capture rules:

- 30-60 seconds.
- Start near room entrance or center.
- Slow 180-360 degree sweep.
- Keep major objects visible for 2-3 seconds from multiple angles.
- Avoid fast panning and motion blur.
- Include corners, posters, furniture edges, textured objects; do not film only blank walls.
- Place a scale reference such as A4 paper, ruler, box, or known laptop dimension.
- Do not commit original room video; copy it under `outputs/.../input/` for local runs.

- [ ] **Step 6: Run tests and commit**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_segment_keyframes.py tests/pipeline/test_run_manual_segmentation.py tests/adapters/test_sam_adapter.py
```

Commit:

```bash
git add src/object3d/pipeline/run_segment_keyframes.py src/object3d/pipeline/segment_keyframes.py tests/pipeline/test_run_segment_keyframes.py docs/runbooks/20260527-room-video-capture-guide.md
git commit -m "feat(#T23): keyframe 객체 segmentation batch 추가" \
  -m "src/object3d/pipeline/run_segment_keyframes.py: prompt manifest를 읽어 frame/object별 segmentation summary를 생성합니다." \
  -m "src/object3d/pipeline/segment_keyframes.py: manual/SAM2 batch segmentation CLI를 추가합니다." \
  -m "docs/runbooks/20260527-room-video-capture-guide.md: 기말 프로젝트용 방 영상 촬영 기준을 기록합니다."
```

---

## T24: Object-Aware Multi-View Fusion

**Purpose:** Merge per-frame object priors for the same object into a single world-space object prior.

**Files:**
- Create: `src/object3d/pipeline/run_fuse_object_priors.py`
- Create: `src/object3d/pipeline/fuse_object_priors.py`
- Test: `tests/pipeline/test_run_fuse_object_priors.py`
- Modify: `src/object3d/reconstruction/fusion.py` only if needed for summaries.

- [ ] **Step 1: Write failing fusion tests**

```python
def test_run_fuse_object_priors_merges_same_object_clouds(tmp_path):
    summary_paths = [
        _write_prior_summary_with_cloud(tmp_path, frame_id=0, offset_x=0.0),
        _write_prior_summary_with_cloud(tmp_path, frame_id=1, offset_x=0.1),
    ]

    summary = run_fuse_object_priors(
        prior_summary_paths=summary_paths,
        output_dir=tmp_path / "fused",
        outlier_filter="radial_percentile",
        outlier_keep_ratio=0.95,
    )

    assert summary["object_id"] == "object_001"
    assert summary["input_prior_count"] == 2
    assert summary["source_frame_ids"] == [0, 1]
    assert Path(summary["point_cloud_ply"]).exists()
    assert Path(summary["bbox_ply"]).exists()
```

- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_fuse_object_priors.py
```

Expected: module missing.

- [ ] **Step 3: Implement prior summary loader**

Use existing `read_ascii_ply` to avoid inventing a PLY parser:

```python
ply = read_ascii_ply(Path(summary["point_cloud_ply"]))
cloud = PointCloudRecord(
    object_id=summary["object_id"],
    points_xyz=np.asarray(ply.vertices, dtype=np.float32),
    source_frame_ids=(int(summary["frame_id"]),),
)
```

- [ ] **Step 4: Fuse and export**

```python
fused_cloud = fuse_point_clouds(clouds)
filtered_cloud, filter_summary = _filter_cloud(...)
prior = fit_oriented_bbox(filtered_cloud)
scene = export_scene_artifacts(filtered_cloud, prior, output_dir)
```

Summary must include `input_prior_count`, `input_point_count`, `filtered_point_count`, `removed_point_count`, `source_frame_ids`, and `dimensions_m`.

- [ ] **Step 5: Add CLI**

`fuse_object_priors.py` accepts repeated `--prior-summary` values:

```bash
PYTHONPATH=src .venv/bin/python -m object3d.pipeline.fuse_object_priors \
  --prior-summary outputs/room/objects/laptop/frame_000000/prior/summary.json \
  --prior-summary outputs/room/objects/laptop/frame_000006/prior/summary.json \
  --output-dir outputs/room/objects/laptop/fused \
  --outlier-filter radial_percentile \
  --outlier-keep-ratio 0.95
```

- [ ] **Step 6: Run tests and commit**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/pipeline/test_run_fuse_object_priors.py tests/reconstruction/test_fusion.py tests/priors/test_bbox.py
```

Commit:

```bash
git add src/object3d/pipeline/run_fuse_object_priors.py src/object3d/pipeline/fuse_object_priors.py tests/pipeline/test_run_fuse_object_priors.py
git commit -m "feat(#T24): 객체별 multi-view point cloud fusion 추가" \
  -m "src/object3d/pipeline/run_fuse_object_priors.py: frame별 object prior를 같은 object_id 기준으로 합치고 최종 bbox를 생성합니다." \
  -m "src/object3d/pipeline/fuse_object_priors.py: prior summary 목록을 받는 fusion CLI를 추가합니다." \
  -m "tests/pipeline/test_run_fuse_object_priors.py: synthetic prior summary와 PLY로 fusion 동작을 검증합니다."
```

---

## T25: Coarse Room Point Cloud And Plane Estimation

**Purpose:** Produce the room-level context required by the final project: coarse point cloud plus rough floor/wall/table plane candidates.

**Files:**
- Create: `src/object3d/reconstruction/plane.py`
- Create: `src/object3d/pipeline/run_room_geometry_summary.py`
- Create: `src/object3d/pipeline/room_geometry_summary.py`
- Test: `tests/reconstruction/test_plane.py`
- Test: `tests/pipeline/test_run_room_geometry_summary.py`

- [ ] **Step 1: Write plane tests**

```python
def test_fit_plane_pca_recovers_horizontal_plane():
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
        dtype=np.float32,
    )

    plane = fit_plane_pca(points)

    assert abs(abs(plane.normal_xyz[2]) - 1.0) < 1e-5
    assert plane.inlier_count == 4
```

- [ ] **Step 2: Write room summary test**

```python
def test_run_room_geometry_summary_exports_downsampled_cloud_and_planes(tmp_path):
    geometry_paths = [_write_geometry_npz(tmp_path, frame_id=0)]

    summary = run_room_geometry_summary(
        geometry_npz_paths=geometry_paths,
        output_dir=tmp_path / "room",
        stride=2,
        max_points=5000,
    )

    assert summary["geometry_count"] == 1
    assert summary["room_point_count"] > 0
    assert Path(summary["room_point_cloud_ply"]).exists()
```

- [ ] **Step 3: Implement plane fitting**

Start with PCA plane fitting for a sampled point set:

```python
centroid = points.mean(axis=0)
centered = points - centroid
_, _, vh = np.linalg.svd(centered, full_matrices=False)
normal = vh[-1].astype(np.float32)
distances = np.abs(centered @ normal)
```

Do not claim semantic labels such as floor or wall automatically. Store `plane_0`, `plane_1`, etc. and label them manually in validation if needed.

- [ ] **Step 4: Implement room cloud sampling**

For each geometry:

```python
mask = np.ones_like(geometry.depth_m, dtype=bool)
cloud = backproject_masked_points(mask, geometry)
sampled = cloud.points_xyz[::stride]
```

Cap the final cloud at `max_points` to keep local rendering and PR artifacts manageable.

- [ ] **Step 5: Run tests and commit**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/reconstruction/test_plane.py tests/pipeline/test_run_room_geometry_summary.py tests/geometry/test_backprojection.py
```

Commit:

```bash
git add src/object3d/reconstruction/plane.py src/object3d/pipeline/run_room_geometry_summary.py src/object3d/pipeline/room_geometry_summary.py tests/reconstruction/test_plane.py tests/pipeline/test_run_room_geometry_summary.py
git commit -m "feat(#T25): coarse room point cloud와 plane summary 추가" \
  -m "src/object3d/reconstruction/plane.py: sampled point cloud에서 rough plane을 추정하는 유틸을 추가합니다." \
  -m "src/object3d/pipeline/run_room_geometry_summary.py: geometry.npz 목록에서 coarse room cloud와 plane summary를 생성합니다." \
  -m "tests/reconstruction/test_plane.py: synthetic plane fitting을 검증합니다."
```

---

## T26: Measurement Evaluation And Final Smoke

**Purpose:** Turn the demo into a graded final project artifact with measurable outputs.

**Files:**
- Create: `src/object3d/pipeline/run_evaluate_object_priors.py`
- Create: `src/object3d/pipeline/evaluate_object_priors.py`
- Test: `tests/pipeline/test_run_evaluate_object_priors.py`
- Create: `docs/validation/20260527-room-object-prior-final-smoke.md`
- Modify: `README.md`
- Modify: `docs/PLAN.md`

- [ ] **Step 1: Define measurement JSON**

Use this format:

```json
{
  "objects": [
    {
      "object_id": "laptop_001",
      "measured_dimensions_m": [0.312, 0.221, 0.016],
      "notes": "MacBook body only, screen excluded"
    }
  ]
}
```

- [ ] **Step 2: Write evaluation test**

```python
def test_run_evaluate_object_priors_compares_fused_summary_to_measurements(tmp_path):
    prior_summary = _write_fused_prior_summary(
        tmp_path,
        object_id="laptop_001",
        dimensions_m=[0.32, 0.22, 0.02],
    )
    measurements = _write_measurements(tmp_path)

    summary = run_evaluate_object_priors(
        prior_summary_paths=[prior_summary],
        measurements_json_path=measurements,
        output_path=tmp_path / "evaluation.json",
    )

    assert summary["object_count"] == 1
    assert summary["objects"][0]["object_id"] == "laptop_001"
    assert summary["objects"][0]["relative_error_percent"]
```

- [ ] **Step 3: Implement evaluation runner**

Load fused prior summaries and measurement JSON. For each object:

```python
errors = dimension_errors(
    np.asarray(prior["dimensions_m"], dtype=np.float32),
    np.asarray(measured["measured_dimensions_m"], dtype=np.float32),
)
```

Write `evaluation.summary.json`.

- [ ] **Step 4: Run final local smoke**

Use the final room video locally:

```bash
PYTHONPATH=src .venv/bin/python -m object3d.pipeline.video_keyframes \
  --video-path outputs/final-room/input/room.mp4 \
  --output-dir outputs/final-room/keyframes \
  --manifest-path outputs/final-room/keyframes/manifest.json \
  --target-fps 0.5
```

Then run VGGT batch, segmentation batch, per-frame priors, fusion, room summary, and evaluation. Keep all generated data in `outputs/final-room/`.

- [ ] **Step 5: Create final validation document**

`docs/validation/20260527-room-object-prior-final-smoke.md` should include:

- Input capture conditions.
- Keyframe count.
- Object list.
- SAM2 overlay contact sheet.
- Coarse room cloud preview.
- Plane summary table.
- Object fused bbox preview.
- Measurement error table.
- Failure analysis for at least one hard object.

Only commit small derived images under `docs/validation/assets/`; do not commit original video or `outputs/`.

- [ ] **Step 6: Run full verification and commit**

```bash
git diff --check
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Commit:

```bash
git add src/object3d/pipeline/run_evaluate_object_priors.py src/object3d/pipeline/evaluate_object_priors.py tests/pipeline/test_run_evaluate_object_priors.py docs/validation/20260527-room-object-prior-final-smoke.md README.md docs/PLAN.md
git commit -m "docs(#T26): 방 영상 기반 객체 3D prior 최종 smoke 정리" \
  -m "src/object3d/pipeline/run_evaluate_object_priors.py: fused prior와 실측값 비교 summary를 생성합니다." \
  -m "docs/validation/20260527-room-object-prior-final-smoke.md: 최종 프로젝트 입력, 결과, 오차, 실패 분석을 기록합니다." \
  -m "README.md: 기말 프로젝트 실행 흐름을 최신 pipeline에 맞게 갱신합니다."
```

---

## Final Demo Acceptance Criteria

- A 30-60 second room video is processed locally without committing the video.
- 8-20 keyframes are extracted and listed in a manifest.
- VGGT geometry exists for the selected keyframes.
- At least 2 objects have frame-level masks, object clouds, fused object cloud, and oriented bbox.
- At least 1 coarse room point cloud preview exists.
- At least 1-3 rough plane candidates are summarized.
- At least 2 objects have measured dimensions and error percentages.
- Final document includes success cases, failure cases, and a clear statement that this is not full room mesh reconstruction.
- Full tests pass with checkpoint-free fake runners.

## PR / T-Unit Sequencing

1. T21 PR: video keyframe extraction.
2. T22 PR: VGGT batch geometry from keyframes.
3. T23 PR: object segmentation batch and capture guide.
4. T24 PR: object-aware multi-view fusion.
5. T25 PR: coarse room cloud and plane summary.
6. T26 PR: measurement evaluation and final validation artifact.

## Risk Controls

- Run local Mac smoke with 8-12 keyframes first.
- Use school RTX 30/40 machine only after local command path is stable.
- Avoid transparent/thin objects as required success cases.
- Use object names that can be measured: laptop body, box, chair seat, desk/table top.
- Add one risk object, such as cup or reflective screen, only for failure analysis.
- Keep generated data in `outputs/`.
- Commit only small derived validation images and markdown.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-27-room-object-3d-prior-final-project.md`.

Recommended execution mode: **Subagent-Driven** for T21-T26, one PR per T-unit. Inline execution is acceptable for T21/T22 if time is tight, but T24/T25 should get review checkpoints because they affect the final project argument.
