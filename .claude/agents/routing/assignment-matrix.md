# 에이전트 배정 매트릭스

작업을 dispatch하기 전에 올바른 owner가 지정됐는지 확인한다.

공용 라우팅은 `agents/routing/`, 조율 규칙은 `agents/coordination/`, worker 템플릿은 `agents/templates/`에 있다.

## 실행 흐름

| 흐름 | 주 담당 | 지원 agent | 필수 skill | 출력 |
|---|---|---|---|---|
| 프로젝트 이해 | Orchestrator Agent | 없음 | `skills/command-routing.md` | 다음 라우팅 |
| 마일스톤 계획 | Research Agent | Integration Agent | `skills/implementation-planning.md` | phase plan과 issue slice |
| 멀티 worker 설정 | Orchestrator Agent | Issue Manager Agent | `skills/task-orchestration.md` | task folder와 worker brief |
| 컨텍스트/메모리 최적화 | Orchestrator Agent | Structure Manager Agent | `skills/context-memory-optimization.md` | compaction과 handoff 정리 |
| 운영 규칙 정리 | Structure Manager Agent | Orchestrator Agent | `skills/folder-structure-management.md` | `rules/` 갱신과 라우터 연결 |
| 비즈니스 로직 판단 | Orchestrator Agent | Structure Manager Agent | `rules/business-logic.md` | MVP 범위 또는 중단 판단 |
| 데이터/artifact 정책 | Evaluation Agent | Structure Manager Agent | `rules/data-and-artifacts.md` | 저장 위치와 커밋 제외 판단 |
| 검증/완료 기준 | Review Orchestrator Agent | Evaluation Agent | `rules/review-and-verification.md` | 완료 주장 가능 여부 |
| Issue/worktree 설정 | Issue Manager Agent | Git Manager Agent | `skills/issue-worktree-workflow.md` | issue, branch, worktree 계획 |
| 촬영 프로토콜 | Data and Capture Agent | Evaluation Agent | `skills/capture-protocol.md` | 촬영 notes와 측정값 |
| SAM tracking | Segmentation Agent | Evaluation Agent | `skills/model-adapter.md` | normalized mask contract |
| depth/pose contract | Geometry Agent | Reconstruction Agent | `skills/geometry-validation.md` | 검증된 geometry contract |
| point cloud fusion | Reconstruction Agent | Geometry Agent | `skills/geometry-validation.md` | object/scene point cloud artifact |
| object prior fitting | Object Prior Agent | Segmentation, Geometry, Evaluation | `skills/object-prior-fitting.md` | bbox, dimension, orientation, confidence |
| experiment/ablation | Evaluation Agent | 관련 domain owner | `skills/experiment-logging.md` | run log와 metric |
| demo evidence | Visualization Agent | Evaluation Agent | `skills/visual-demo.md` | 보고서용 screenshot/view |
| 폴더 구조 | Structure Manager Agent | Integration Agent | `skills/folder-structure-management.md` | layout decision |
| 코드 리뷰 | Review Orchestrator Agent | domain reviewer | `skills/code-review-stack.md` | finding과 review result |
| PR comment | Review Orchestrator Agent | Git Manager Agent | `skills/pr-review-commenting.md` | PR-safe review comment |
| 병합 전략 | PR Merge Orchestrator Agent | Git Manager, Review Orchestrator | `skills/pr-merge-orchestration.md` | merge order 또는 decision brief |
| conflict 결정 | Orchestrator Agent | PR Merge Orchestrator Agent | `skills/decision-brief.md` | 사용자 선택지 |
| 실패 학습 | Failure Recorder Agent | 관련 domain owner | `skills/failure-recording.md` | failure note |

## 하지 말 것

- 사용자 요청이 모호할 때 이 매트릭스를 `agents/routing/command-router.md` 대신 사용하지 않는다.
- supporting agent를 같은 writable artifact의 공동 owner로 만들지 않는다.
- 멀티 worker 구현에서 task folder를 생략하지 않는다.
- geometry, measurement, external model contract가 바뀌었는데 리뷰를 생략하지 않는다.

## 흐름 점검

dispatch 전 다음을 답한다.

```text
작업:
주 담당:
지원 agent:
스킬:
작업 폴더:
Issue/worktree 필요 여부:
리뷰 담당:
병합 담당:
사용자 승인 필요 여부:
```
