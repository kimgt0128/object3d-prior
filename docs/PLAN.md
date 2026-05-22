# Current Implementation Plan

> **Superpowers:** 큰 기능을 시작할 때는 `using-superpowers`로 관련 skill을 확인한다. 구현은 TDD를 따른다. 이 프로젝트에서는 과한 하네스 확장을 피하고 `docs/PLAN.md` 하나만 현재 계획으로 유지한다.

## 현재 상태

- Issue #10 / PR #11까지 병합되어 mock MVP를 CLI로 실행할 수 있다.
- 현재 실행 가능 명령:

```bash
PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp
```

- 아직 실제 SAM/SAM2 모델은 붙어 있지 않다.
- 다음 병목은 실제 모델 의존성을 강제로 설치하지 않으면서 `MaskRecord` contract로 변환할 adapter 경계를 만드는 것이다.

## 이번 작업: Issue #12 SAM/SAM2 adapter contract

목표는 실제 SAM/SAM2 predictor를 나중에 연결할 수 있도록 segmentation adapter contract를 추가하는 것이다.

이번 작업에서 할 일:

- prompt contract 정의
- predictor 주입 방식으로 SAM-like output을 `MaskRecord`로 변환
- SAM/SAM2 패키지가 없을 때 명확한 optional dependency error 제공
- mock downstream pipeline은 그대로 유지

이번 작업에서 하지 않을 일:

- 모델 가중치 다운로드
- GPU 실행
- 실제 이미지 demo
- depth/pose adapter 변경

## 작업 범위

수정/생성:

- `src/object3d/adapters/segmentation/sam.py`
- `tests/adapters/test_sam_adapter.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- `src/object3d/adapters/geometry/**`
- `src/object3d/geometry/**`
- `src/object3d/reconstruction/**`
- `project/`, `cv_tutorial/`, `reference/`

## 실행 순서

- [x] Issue #12 생성
- [x] `feat/12-sam-adapter-contract` 브랜치 생성
- [x] failing test 작성
- [x] SAM/SAM2 adapter contract 구현
- [x] README 갱신
- [x] `python3 -m pytest -q` 실행
- [x] `python3 -m compileall src` 실행
- [x] `serena project health-check` 실행
- [ ] 커밋, 푸시, PR 생성

## 다음 후보

이번 작업 이후에 선택할 수 있는 다음 단계:

1. 실제 image frame + manual box/prompt 기반 mask input 연결
2. SAM v1 또는 SAM2 중 하나를 실제 dependency로 설치해 smoke demo 구성
3. Open3D/Rerun viewer 추가
4. bbox를 axis-aligned에서 PCA 기반 oriented bbox로 확장
