# 향후 코드 모듈 구조 계획

이 파일은 실제 source code를 만들기 시작할 때만 연다. 지금은 project coordination 문서와 실제 구현 코드를 섞지 않기 위한 설계 기준이다.

## 먼저 만들지 말 것

- 코드가 없는데 거대한 package tree부터 만들지 않는다.
- full-room reconstruction 전용 module부터 만들지 않는다.
- 외부 모델별 raw output format을 전체 코드에 퍼뜨리지 않는다.
- demo UI가 core geometry logic을 직접 호출하게 하지 않는다.

## 권장 최상위 구조

```text
configs/
  default.yaml
  models/
data/
  raw/
  interim/
  processed/
  results/
src/object3d/
  capture/
  adapters/
  geometry/
  reconstruction/
  priors/
  evaluation/
  visualization/
  pipeline/
scripts/
tests/
docs/
.claude/
```

## 핵심 모듈 경계

| 모듈 | 책임 | 넘겨야 할 출력 |
|---|---|---|
| `capture/` | frame sampling, metadata, manual measurement 정리 | frame manifest, capture metadata |
| `adapters/segmentation/` | SAM/SAM2/Grounded SAM output 정규화 | frame id, object id, binary mask, confidence |
| `adapters/geometry/` | MapAnything/VGGT/COLMAP output 정규화 | depth, intrinsics, pose, convention |
| `geometry/` | back-projection, scale alignment, pose sanity check | per-frame masked point |
| `reconstruction/` | object point fusion, outlier filtering | object point cloud |
| `priors/` | bbox, dimension, orientation, placement constraint | object prior report |
| `evaluation/` | 실측값 비교, ablation, threshold 기록 | metric table, failure analysis |
| `visualization/` | mask overlay, point cloud, bbox, demo evidence | screenshot, Rerun/Open3D artifact |
| `pipeline/` | 단계 연결과 config-driven 실행 | end-to-end run summary |

## 데이터 계약

초기에는 복잡한 class hierarchy보다 작고 명시적인 schema를 우선한다.

```text
FrameRecord:
  frame_id
  image_path
  timestamp
  camera_metadata

MaskRecord:
  frame_id
  object_id
  mask_path
  confidence
  prompt_type
  warning

GeometryRecord:
  frame_id
  depth_path
  intrinsics
  pose
  coordinate_convention
  scale_note

ObjectPrior:
  object_id
  point_cloud_path
  bbox_type
  dimensions_cm
  center
  orientation
  confidence
  placement_note
```

## 첫 구현 순서

1. `capture/`와 `adapters/segmentation/`으로 mask overlay artifact를 만든다.
2. `adapters/geometry/`와 `geometry/`로 1프레임 masked point cloud를 만든다.
3. `reconstruction/`으로 2프레임 fusion만 먼저 검증한다.
4. `priors/`로 oriented bounding box와 치수를 낸다.
5. `evaluation/`으로 수동 측정값과 비교한다.
6. `visualization/`으로 발표용 evidence를 만든다.

## 리뷰 게이트

- module boundary가 바뀌면 `agents/routing/command-router.md`와 agent ownership을 확인한다.
- adapter contract가 바뀌면 downstream geometry와 prior code를 함께 검토한다.
- data path convention이 바뀌면 experiment log와 visualization path도 같이 갱신한다.
