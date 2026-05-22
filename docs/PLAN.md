# Current Implementation Plan

> **Superpowers:** 큰 기능을 시작할 때는 `using-superpowers`로 관련 skill을 확인한다. 구현은 TDD를 따른다. 이 프로젝트에서는 과한 하네스 확장을 피하고 `docs/PLAN.md` 하나만 현재 계획으로 유지한다.

## 현재 상태

- Issue #12 / PR #13까지 병합되어 SAM/SAM2 predictor output을 `MaskRecord`로 바꾸는 adapter contract가 들어왔다.
- 아직 실제 SAM/SAM2 dependency, checkpoint, GPU 실행은 붙이지 않았다.
- 현재 필요한 다음 단계는 실제 모델보다 먼저 **이미지와 수동 prompt의 입력/출력 포맷**을 고정하는 것이다.

## 이번 작업: Issue #14 image + manual prompt segmentation

목표는 이미지 한 장과 prompt JSON을 입력받아 segmentation mask 산출물을 생성하는 실행 흐름을 추가하는 것이다.

예상 실행:

```bash
PYTHONPATH=src python3 -m object3d.pipeline.segment_image \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/manual-segmentation
```

기대 산출물:

- `mask.npy`
- `summary.json`
- `overlay.png`

## 작업 범위

수정/생성:

- `src/object3d/adapters/segmentation/manual.py`
- `src/object3d/visualization/mask_overlay.py`
- `src/object3d/pipeline/run_manual_segmentation.py`
- `src/object3d/pipeline/segment_image.py`
- `tests/adapters/test_manual_segmentation.py`
- `tests/visualization/test_mask_overlay.py`
- `tests/pipeline/test_run_manual_segmentation.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- real SAM/SAM2 dependency 설치
- geometry/depth/pose/reconstruction 모듈
- Open3D/Rerun viewer
- `project/`, `cv_tutorial/`, `reference/`

## 실행 순서

- [x] Issue #14 생성
- [x] `feat/14-manual-prompt-segmentation` 브랜치 생성
- [x] failing test 작성
- [x] prompt parser/manual predictor 구현
- [x] mask overlay export 구현
- [x] image segmentation pipeline/CLI 구현
- [x] README 갱신
- [x] `python3 -m pytest -q` 실행
- [x] `python3 -m compileall src` 실행
- [x] CLI smoke test 실행
- [x] `serena project health-check` 실행
- [ ] 커밋, 푸시, PR 생성

## 다음 후보

이번 작업 이후에 선택할 수 있는 다음 단계:

1. SAM v1 또는 SAM2 중 하나를 실제 dependency로 설치해 smoke demo 구성
2. Open3D/Rerun viewer 추가
3. bbox를 axis-aligned에서 PCA 기반 oriented bbox로 확장
4. MapAnything/VGGT depth/pose adapter contract 추가
