# Current Implementation Plan

> **Superpowers:** 큰 기능을 시작할 때는 `using-superpowers`로 관련 skill을 확인한다. 구현은 TDD를 따른다. PR은 T 단위로 올리고, 커밋은 세부 작업 단위로 쌓는다.

## 현재 상태

- Issue #14 / PR #15까지 병합되어 이미지 + 수동 prompt로 `mask.npy`, `overlay.png`, `summary.json`을 만들 수 있다.
- SAM/SAM2 predictor output을 `MaskRecord`로 변환하는 adapter contract도 존재한다.
- 아직 실제 SAM2 dependency, checkpoint, config를 받아 실행하는 CLI 경로는 없다.

## 이번 작업: Issue #16 T2 SAM2 smoke path

목표는 기존 `segment_image` CLI에 SAM2 backend 실행 경로를 추가하는 것이다.

실제 실행 예시:

```bash
PYTHONPATH=src python3 -m object3d.pipeline.segment_image \
  --backend sam2 \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/sam2-segmentation \
  --checkpoint-path checkpoints/sam2.1_hiera_tiny.pt \
  --config-path configs/sam2.1/sam2.1_hiera_t.yaml \
  --device cpu
```

## 작업 범위

수정/생성:

- `src/object3d/pipeline/run_manual_segmentation.py`
- `src/object3d/pipeline/segment_image.py`
- `tests/pipeline/test_run_manual_segmentation.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- SAM2 dependency 자동 설치
- checkpoint/config 다운로드 및 커밋
- geometry/depth/pose/reconstruction 모듈
- Open3D/Rerun viewer
- `project/`, `cv_tutorial/`, `reference/`

## 실행 순서

- [x] Issue #16 생성
- [x] `feat/16-t2-sam2-smoke-path` 브랜치 생성
- [x] failing test 작성
- [x] `segment_image` backend 옵션 추가
- [x] SAM2 predictor loader 연결
- [x] missing dependency/checkpoint/config 에러 처리
- [x] README 갱신
- [x] `python3 -m pytest -q` 실행
- [x] `python3 -m compileall src` 실행
- [x] manual CLI smoke test 실행
- [x] `serena project health-check` 실행
- [x] 커밋, 푸시, PR 생성

## 참고

- Meta SAM2 공식 README 기준 image prediction은 `build_sam2(model_cfg, checkpoint)`와 `SAM2ImagePredictor`를 사용한다.
- 이 PR은 실제 SAM2 설치를 강제하지 않고, 사용자가 dependency/checkpoint/config를 제공했을 때 실행 가능한 경로를 만든다.

## 다음 후보

1. SAM2 실제 checkpoint로 로컬 smoke 실행
2. Open3D/Rerun viewer 추가
3. bbox를 axis-aligned에서 PCA 기반 oriented bbox로 확장
4. MapAnything/VGGT depth/pose adapter contract 추가
