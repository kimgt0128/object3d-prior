# CLAUDE.md

`.claude/` 경량 하네스의 진입점.

## 1. Project Overview

**Object3D Prior** — SAM 계열 모델의 2D 객체 mask를 depth·camera pose·point cloud와 결합해, 객체의 3D 위치·크기·방향·confidence·배치 가능성을 추정하는 컴퓨터 비전 프로젝트. 상세는 `docs/README.md`(단일 출처).

## 2. Goal

- **최종:** 스마트폰 촬영만으로 객체의 3D 정보(위치·크기·방향·confidence·배치)를 제공.
- **현재:** No-Training MVP — 단일 객체 하나로 T1~T8 end-to-end. 방 전체 복원·학습은 범위 밖.
- **단계:** T1 capture 안정화 (CLI 진입점, non-integer FPS, unknown frame count).

## 3. Architecture Summary

`T1 Capture → T2 Segmentation → T3 Geometry → T4 Back-Projection → T5 Fusion → T6 Prior Fitting → T7 Evaluation → T8 Visualization`

코드는 `src/object3d/` 아래 모듈(`capture/ adapters/ geometry/ reconstruction/ priors/ evaluation/ visualization/ pipeline/`). 외부 모델 raw output은 **adapter**로 표준 record로 정규화한 뒤에만 downstream에 넘긴다.

## 4. Directory Routing

| 작업 | 먼저 볼 곳 |
|---|---|
| 프로젝트 이해 | `docs/README.md` |
| 코드 | `src/object3d/<module>/` |
| 설정 / 데이터 / 테스트 | `configs/` / `data/` / `tests/` |
| 작업 프로세스 | `.claude/skills/workflow.md` |
| 설계·계획 | `docs/superpowers/{specs,plans}/` |

하네스 폴더 `.claude/`: `agents/` `rules/` `hooks/` `skills/` `commands/`. `skills/`만 내용이 있고 나머지는 **의도적으로 비어 있다**. 각 폴더는 그 기능이 실제로 필요해질 때 항목 하나씩 사용자 승인 후 채운다 (§6).

## 5. Skill & Agent Routing

작업 프로세스와 서브에이전트 할당 규칙은 `.claude/skills/workflow.md`가 정한다. 요약:

- 프로세스는 **superpowers 스킬**에 위임한다 — 설계 `brainstorming`/`writing-plans`, 구현 `test-driven-development`, 디버깅 `systematic-debugging`, 완료 전 `verification-before-completion`, 리뷰 `requesting-code-review`.
- 메인 세션 = orchestrator. 서브에이전트는 `implementer`(구현)·`reviewer`(리뷰) 둘이며, 필요해질 때 `agents/`에 하나씩 추가한다. 넓은 탐색은 빌트인 `Explore`.

## 6. Core Rules

- 작업 전 `docs/README.md`로 목표·단계(T1~T8)·수정 범위·안 할 것·검증 방법을 정한다.
- 모델 출력(mask·depth·pose)은 정답이 아니라 noisy measurement다.
- raw output은 adapter로 표준 record로 변환 후 downstream에 넘긴다.
- 작은 단위로 구현하고 테스트/시각 검증 가능한 단위로 끝낸다.
- 불확실한 설계·아키텍처·모델 선택은 결정하지 않고 사용자에게 올린다.
- 하네스 자동화(agent/skill/hook/command/rule)는 미리 만들지 않는다. 반복 고통 확인 시 하나씩 승인받아 추가.

## 7. Coding Conventions

- Python. 단계 간 데이터는 명시적 schema record로 (`FrameRecord`, `MaskRecord`, `GeometryRecord`, `ObjectPrior` — `docs/README.md` 데이터 계약 참고).
- 모듈 경계를 지킨다. demo/UI가 core geometry를 직접 소유하지 않는다.
- 작고 책임이 분명한 파일을 선호한다. (lint/format 도구는 미확정 — 정해지면 갱신.)

## 8. Documentation Policy

- 프로젝트 상세: `docs/README.md` (단일 출처)
- 설계·계획: `docs/superpowers/{specs,plans}/`
- 실험 결과·metric: 실험 로그 / `data/results/` (코드와 분리)
- 같은 규칙을 여러 문서에 중복하지 않는다.

## 9. Verification

- 코드: `pytest tests/<module>/` (테스트 인프라는 capture부터 구성 중).
- geometry·measurement: 1프레임 point cloud → 2프레임 fusion 순으로 시각 검증.
- 시각 결과는 artifact/screenshot 경로를 남긴다.
- 완료 주장 전 `verification-before-completion`으로 실제 명령 출력을 확인한다.

## 10. Do Not

- 방 전체 복원·하네스 자동화·문서 구조를 먼저 키우지 않는다. 첫 목표는 단일 객체.
- raw video·dataset·checkpoint·cache·secret·큰 산출물을 git에 넣지 않는다.
- 모델 출력을 ground truth로 취급하지 않는다. 수동 실측값 없이 정확도를 주장하지 않는다.
- mask overlay 검증 없이 geometry로 넘어가지 않는다. 실패 frame을 숨기지 않는다.
- 이 진입점 문서(`CLAUDE.md`)를 사용자 승인 없이 수정·삭제하지 않는다.
- `.claude-legacy/`(옛 하네스)를 새 작업에서 읽지 않는다.
