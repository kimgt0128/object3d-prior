# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. 지금 단계는 빠르게 기본 기능을 끝까지 연결한 뒤 전체 테스트로 디버깅한다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, evaluation, PLY export가 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- SAM2 tiny checkpoint 기반 실제 CLI smoke는 통과했다.
- mock MVP는 end-to-end로 summary와 point cloud PLY를 생성한다.

## 이번 작업: Issue #20 T6 PCA 기반 oriented bbox 및 크기 측정

목표는 axis-aligned bbox만 쓰던 object prior fitting을 PCA 기반 oriented bbox까지 확장하는 것이다.
객체가 회전된 상태에서도 주축 기준 크기를 계산할 수 있어야 한다.

## 작업 범위

수정/생성:

- `src/object3d/priors/bbox.py`
- `tests/priors/test_bbox.py`
- `src/object3d/pipeline/run_mock_mvp.py`
- `tests/pipeline/test_run_mock_mvp.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- SAM2 추가 기능
- 실제 MapAnything/VGGT depth/pose 연동
- Open3D/Rerun viewer
- checkpoint/config 파일 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 구현 내용

- 기존 `fit_axis_aligned_bbox()`는 유지한다.
- `fit_oriented_bbox()`를 추가한다.
- PCA eigenvector를 object axes로 사용한다.
- point cloud를 PCA local coordinate로 투영한 뒤 min/max extent로 `dimensions_m`을 계산한다.
- axes determinant가 음수면 마지막 축을 뒤집어 right-handed frame을 유지한다.
- mock MVP는 `fit_oriented_bbox()`를 기본 사용하고 summary에 `bbox_type: oriented`를 남긴다.

## 실행 순서

- [x] Issue #20 생성
- [x] `feat/20-oriented-bbox` 브랜치 생성
- [x] 회전된 synthetic cuboid 테스트 추가
- [x] PCA 기반 oriented bbox 구현
- [x] mock MVP를 oriented bbox로 전환
- [x] 전체 테스트 실행
- [x] mock MVP CLI smoke 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

- `PYTHONPATH=src python3 -m pytest tests/priors/test_bbox.py -q` → 2 passed
- `PYTHONPATH=src python3 -m pytest tests/pipeline/test_run_mock_mvp.py tests/priors/test_bbox.py -q` → 3 passed
- `PYTHONPATH=src python3 -m pytest -q` → 67 passed
- `python3 -m compileall src` → 통과
- `PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp-oriented` → `bbox_type: oriented`

## 다음 후보

1. Open3D/Rerun viewer 추가
2. 실제 사용자 이미지 1장으로 SAM2 prompt smoke 실행
3. MapAnything/VGGT depth/pose adapter contract 추가
