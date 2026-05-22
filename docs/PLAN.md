# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. 지금 단계는 빠르게 기본 기능을 끝까지 연결한 뒤 전체 테스트로 디버깅한다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- SAM2 tiny checkpoint 기반 실제 CLI smoke는 통과했다.
- mock MVP는 summary, point cloud PLY, oriented bbox PLY, scene manifest를 생성한다.

## 이번 작업: Issue #24 T8 scene manifest optional viewer CLI

목표는 Issue #22에서 만든 `scene_manifest.json`을 실제로 소비하는 viewer CLI를 추가하는 것이다.
기본 환경에서는 dependency 없이 summary를 출력하고, Rerun이 설치된 경우에만 lazy import로 3D point cloud와 oriented bbox를 로그한다.

## 작업 범위

수정/생성:

- `src/object3d/visualization/view_scene.py`
- `tests/visualization/test_view_scene.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- Rerun/Open3D를 필수 dependency로 추가
- GUI viewer 자체 구현
- SAM2/MapAnything/VGGT 추가 연동
- checkpoint/config 파일 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 구현 내용

- `load_scene_summary()`로 manifest와 asset 존재 여부를 확인한다.
- `read_ascii_ply()`로 현재 export PLY의 vertices/edges를 읽는다.
- `view_scene(..., backend="summary")`로 dependency 없는 summary backend를 제공한다.
- `view_scene(..., backend="rerun")`으로 optional Rerun backend를 제공한다.
- Rerun이 없으면 `OptionalViewerDependencyError`로 명확히 실패한다.
- `python -m object3d.visualization.view_scene` CLI를 추가한다.

## 실행 순서

- [x] Issue #24 생성
- [x] `feat/24-optional-scene-viewer` 브랜치 생성
- [x] scene summary 테스트 추가
- [x] fake rerun module 기반 lazy backend 테스트 추가
- [x] viewer CLI 테스트 추가
- [x] summary/rerun backend 구현
- [x] 전체 테스트 실행
- [x] mock MVP → viewer summary smoke 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

- `PYTHONPATH=src python3 -m pytest tests/visualization/test_view_scene.py -q` → 6 passed
- `PYTHONPATH=src python3 -m pytest -q` → 76 passed
- `python3 -m compileall src` → 통과
- `PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp-viewer` → scene artifact 생성
- `PYTHONPATH=src python3 -m object3d.visualization.view_scene --manifest outputs/mock-mvp-viewer/scene_manifest.json --backend summary` → asset 존재 summary 출력

## 다음 후보

1. 실제 사용자 이미지 1장으로 SAM2 prompt smoke 실행
2. MapAnything/VGGT depth/pose adapter contract 추가
3. Rerun 설치 환경에서 실제 viewer 렌더링 확인
