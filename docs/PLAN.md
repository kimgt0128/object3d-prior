# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. PR 설명은 어려운 용어를 풀어서 쓴다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- SAM2 tiny checkpoint 기반 실제 CLI smoke는 통과했다.
- mock MVP는 summary, point cloud PLY, oriented bbox PLY, scene manifest를 생성한다.
- scene manifest는 summary backend와 Rerun lazy backend로 열 수 있다.

## 이번 작업: Issue #28 T9 segmentation mask에서 3D object prior 생성

목표는 `segment_image`가 만든 2D mask 결과를 바로 3D prior 파이프라인에 넣는 것이다.
쉽게 말하면 "이미지에서 객체를 잘라낸 결과"를 "3D 점구름과 크기 추정 결과"로 바꾸는 연결 다리를 만든다.

## 작업 범위

수정/생성:

- `src/object3d/pipeline/run_prior_from_mask.py`
- `src/object3d/pipeline/prior_from_mask.py`
- `tests/pipeline/test_run_prior_from_mask.py`
- `src/object3d/geometry/backprojection.py`
- `tests/geometry/test_backprojection.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- 실제 MapAnything/VGGT depth/pose 연결
- SAM2 기능 추가
- Rerun/Open3D 추가 기능
- output 산출물 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 구현 내용

- segmentation `summary.json`에서 `mask.npy`, object id, frame id, confidence를 읽는다.
- `mask.npy`를 `MaskRecord`로 복원한다.
- 임시 `--depth-m` 값으로 mock depth를 만든다.
- mask 영역 pixel만 3D point로 역투영한다.
- oriented bbox와 scene manifest를 생성한다.
- `python -m object3d.pipeline.prior_from_mask` CLI를 추가한다.
- smoke 중 발견한 back-projection warning을 `R @ X + t` 계산으로 제거한다.

## 실행 순서

- [x] Issue #28 생성
- [x] `feat/28-prior-from-segmentation-mask` 브랜치 생성
- [x] segmentation summary 기반 테스트 추가
- [x] mask → mock depth → point cloud → bbox → scene manifest 구현
- [x] CLI 추가
- [x] back-projection warning 제거
- [x] 전체 테스트 실행
- [x] manual segmentation → prior-from-mask smoke 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

- `PYTHONPATH=src python3 -m pytest tests/pipeline/test_run_prior_from_mask.py -q` → 2 passed
- `PYTHONPATH=src python3 -m pytest tests/geometry/test_backprojection.py tests/pipeline/test_run_prior_from_mask.py -q` → 5 passed
- `PYTHONPATH=src python3 -m pytest -q` → 81 passed
- `python3 -m compileall src` → 통과
- `segment_image`로 mask 생성 후 `prior_from_mask`로 3D prior 생성 smoke → 통과

## 다음 후보

1. 실제 사용자 이미지 1장으로 SAM2 → prior-from-mask smoke 실행
2. MapAnything/VGGT depth/pose adapter contract 추가
3. Rerun GUI spawn 화면 검증
