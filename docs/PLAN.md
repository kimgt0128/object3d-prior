# Current Implementation Plan

> **Superpowers:** 큰 기능을 시작할 때는 `using-superpowers`로 관련 skill을 확인한다. 구현 계획 실행은 `executing-plans`를 기준으로 하되, 이 프로젝트에서는 과한 하네스 확장을 피하고 `docs/PLAN.md` 하나만 현재 계획으로 유지한다.

## 현재 상태

- PR #9가 `main`에 병합되어 mock 기반 downstream MVP가 들어왔다.
- 구현된 흐름:
  `mock mask -> mock depth/pose -> masked back-projection -> point cloud fusion -> bbox -> evaluation -> PLY export`
- 다음 병목은 실제 모델 연동이 아니라, 현재 MVP를 명령 한 번으로 실행하고 산출물을 확인하는 루프가 없는 점이다.

## 이번 작업: Issue #10 mock MVP CLI

목표는 기존 `run_mock_mvp`를 터미널에서 실행 가능한 작은 CLI로 감싸는 것이다.

```text
PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp
```

기대 산출물:

- `object_001_cloud.ply`
- `summary.json`
- stdout에 JSON 요약 출력

## 작업 범위

수정/생성:

- `src/object3d/pipeline/cli.py`
- `src/object3d/pipeline/__main__.py`
- `tests/pipeline/test_cli.py`
- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- real SAM/SAM2 adapter
- real MapAnything/VGGT/COLMAP adapter
- Open3D/Rerun interactive visualization
- `project/`, `cv_tutorial/`, `reference/`

## 실행 순서

- [x] Issue #10 생성
- [x] `feat/10-mock-mvp-cli` 브랜치 생성
- [x] CLI 테스트 작성
- [x] CLI 구현
- [x] README에 실행 방법 추가
- [x] `python3 -m pytest -q` 실행
- [x] CLI smoke test 실행
- [ ] 커밋, 푸시, PR 생성

## 다음 후보

이번 작업 이후에 선택할 수 있는 다음 단계:

1. SAM/SAM2 adapter contract와 optional lazy import 추가
2. 실제 image frame + manual box/prompt 기반 mask input 연결
3. Open3D/Rerun viewer 추가
4. bbox를 axis-aligned에서 PCA 기반 oriented bbox로 확장
