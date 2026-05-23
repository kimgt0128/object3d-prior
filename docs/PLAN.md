# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. 지금 단계는 빠르게 기본 기능을 끝까지 연결한 뒤 전체 테스트로 디버깅한다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- SAM2 tiny checkpoint 기반 실제 CLI smoke는 통과했다.
- mock MVP는 summary, point cloud PLY, oriented bbox PLY, scene manifest를 생성한다.
- scene manifest는 summary backend와 Rerun lazy backend로 열 수 있다.

## 이번 작업: Issue #26 T8 실제 Rerun viewer smoke 검증

목표는 fake Rerun 테스트를 넘어 실제 `rerun-sdk` 설치 환경에서 viewer backend를 검증하는 것이다.
GUI spawn만 의존하지 않고, 재현 가능한 `.rrd` recording 저장까지 지원한다.

## 작업 범위

수정/생성:

- `src/object3d/visualization/view_scene.py`
- `tests/visualization/test_view_scene.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- Rerun/Open3D를 필수 dependency로 추가
- Open3D backend 추가
- SAM2/MapAnything/VGGT 추가 연동
- checkpoint/config/output 산출물 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 구현 내용

- `view_scene(..., backend="rerun", save_rrd=...)` 옵션을 추가한다.
- CLI에 `--save-rrd`를 추가한다.
- Rerun backend에서 `rr.init()` 이후 `rr.save()`를 호출해 recording 파일을 저장한다.
- summary JSON에 `rerun_rrd` 경로를 남긴다.
- `.venv`에 `rerun-sdk`를 설치해 실제 backend smoke를 수행한다.

## 실행 순서

- [x] Issue #26 생성
- [x] `chore/26-rerun-viewer-smoke` 브랜치 생성
- [x] `.venv`에 `rerun-sdk` 설치
- [x] 실제 Rerun backend smoke 실행
- [x] `--save-rrd` failing test 추가
- [x] `--save-rrd` 구현
- [x] 실제 `.rrd` recording 생성 확인
- [x] 전체 테스트 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

- `uv pip install --python .venv/bin/python rerun-sdk` → `rerun-sdk==0.32.2` 설치
- `PYTHONPATH=src .venv/bin/python -m object3d.pipeline --output-dir outputs/mock-mvp-rerun-recording` → scene artifact 생성
- `PYTHONPATH=src .venv/bin/python -m object3d.visualization.view_scene --manifest outputs/mock-mvp-rerun-recording/scene_manifest.json --backend rerun --app-id object3d-prior-smoke --save-rrd outputs/mock-mvp-rerun-recording/object3d-prior-smoke.rrd` → 통과
- `outputs/mock-mvp-rerun-recording/object3d-prior-smoke.rrd` 생성 확인
- `PYTHONPATH=src python3 -m pytest -q` → 78 passed
- `PYTHONPATH=src .venv/bin/python -m pytest tests/visualization/test_view_scene.py -q` → 8 passed
- `python3 -m compileall src` → 통과

## 다음 후보

1. 실제 사용자 이미지 1장으로 SAM2 prompt smoke 실행
2. MapAnything/VGGT depth/pose adapter contract 추가
3. Rerun GUI spawn 화면 검증
