# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. 구현은 가능한 한 TDD로 진행한다.

## 현재 상태

- Issue #16 / PR #17까지 병합되어 `segment_image` CLI에서 `manual`과 `sam2` backend를 선택할 수 있다.
- `sam2` backend는 `checkpoint_path`, `config_path`, `device`를 받아 실제 SAM2 predictor를 lazy import로 생성한다.
- 기본 mock/manual pipeline은 SAM2 설치 없이도 계속 동작한다.

## 이번 작업: Issue #18 T2 SAM2 로컬 smoke 검증

목표는 실제 SAM2 dependency와 tiny checkpoint를 로컬에 준비한 뒤, 기존 CLI가 실제 predictor까지 호출되는지 확인하는 것이다.

## 작업 범위

수정/생성:

- `src/object3d/adapters/segmentation/sam.py`
- `tests/adapters/test_sam_adapter.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- checkpoint/config 파일 커밋
- SAM2 dependency를 필수 dependency로 승격
- geometry/depth/pose/reconstruction 모듈
- Open3D/Rerun viewer
- `project/`, `cv_tutorial/`, `reference/`

## 발견한 이슈

SAM2의 `build_sam2(model_cfg, checkpoint)`는 package config search path 기준의 상대 config 이름을 기대한다.
설치된 package 내부 config의 절대 경로를 그대로 넘기면 Hydra가 primary config를 찾지 못한다.

따라서 `sam2` package 내부 absolute config path는 다음 형태로 정규화한다.

```text
/.../site-packages/sam2/configs/sam2.1/sam2.1_hiera_t.yaml
→ configs/sam2.1/sam2.1_hiera_t.yaml
```

## 실행 순서

- [x] Issue #18 생성
- [x] `chore/18-t2-sam2-local-smoke` 브랜치 생성
- [x] Python 3.11 기반 `.venv` 생성
- [x] `torch`, `torchvision`, `opencv-python`, `sam2` 설치
- [x] `sam2.1_hiera_tiny.pt` checkpoint 다운로드
- [x] SAM2 import 및 MPS 사용 가능 여부 확인
- [x] absolute config path 실패 재현
- [x] failing test 작성
- [x] package 내부 absolute config path 정규화 구현
- [x] 실제 SAM2 CLI smoke 실행
- [x] 상대 config path 형태로 실제 SAM2 CLI smoke 실행
- [x] 전체 테스트 실행
- [ ] 커밋, 푸시, PR 생성

## 검증 결과

실제 SAM2 tiny checkpoint smoke 결과:

```json
{
  "backend": "sam2",
  "confidence": 0.9909150004386902,
  "mask_shape": [256, 256],
  "mask_pixels": 20959
}
```

산출물은 `outputs/sam2-smoke/`에 생성되며, `outputs/`는 git에 커밋하지 않는다.

## 다음 후보

1. 실제 사용자 이미지 1장으로 SAM2 prompt smoke 실행
2. Open3D/Rerun viewer 추가
3. bbox를 axis-aligned에서 PCA 기반 oriented bbox로 확장
4. MapAnything/VGGT depth/pose adapter contract 추가
