# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. 지금 단계는 빠르게 기본 기능을 끝까지 연결한 뒤 전체 테스트로 디버깅한다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- SAM2 tiny checkpoint 기반 실제 CLI smoke는 통과했다.
- mock MVP는 end-to-end로 summary와 point cloud PLY를 생성한다.

## 이번 작업: Issue #22 T8 3D scene visualization artifact 생성

목표는 Open3D/Rerun viewer를 붙이기 전에, 현재 mock MVP 결과를 3D로 확인할 수 있는 경량 산출물 계약을 만드는 것이다.
viewer dependency를 필수로 추가하지 않고도 point cloud와 oriented bbox를 함께 확인할 수 있어야 한다.

## 작업 범위

수정/생성:

- `src/object3d/visualization/export.py`
- `tests/visualization/test_export.py`
- `src/object3d/pipeline/run_mock_mvp.py`
- `tests/pipeline/test_run_mock_mvp.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- Open3D/Rerun dependency 필수 추가
- GUI viewer 구현
- SAM2/MapAnything/VGGT 추가 연동
- checkpoint/config 파일 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 구현 내용

- `oriented_bbox_corners()`로 `ObjectPrior`의 8개 bbox corner를 계산한다.
- `export_oriented_bbox_ply()`로 bbox edge가 포함된 ASCII PLY를 저장한다.
- `export_scene_artifacts()`로 point cloud PLY, bbox PLY, scene manifest JSON을 한 번에 생성한다.
- mock MVP는 `summary.json`에 `point_cloud_ply`, `bbox_ply`, `scene_manifest_json` 경로를 함께 남긴다.

## 실행 순서

- [x] Issue #22 생성
- [x] `feat/22-scene-visualization-artifacts` 브랜치 생성
- [x] bbox corners/edge PLY 테스트 추가
- [x] scene manifest 테스트 추가
- [x] visualization artifact 구현
- [x] mock MVP에 scene artifact 연결
- [x] 전체 테스트 실행
- [x] mock MVP CLI smoke 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

- `PYTHONPATH=src python3 -m pytest tests/visualization/test_export.py -q` → 4 passed
- `PYTHONPATH=src python3 -m pytest tests/pipeline/test_run_mock_mvp.py tests/visualization/test_export.py -q` → 5 passed
- `PYTHONPATH=src python3 -m pytest -q` → 70 passed
- `python3 -m compileall src` → 통과
- `PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp-scene` → `point_cloud_ply`, `bbox_ply`, `scene_manifest_json` 생성

## 다음 후보

1. Open3D 또는 Rerun optional viewer CLI 추가
2. 실제 사용자 이미지 1장으로 SAM2 prompt smoke 실행
3. MapAnything/VGGT depth/pose adapter contract 추가
