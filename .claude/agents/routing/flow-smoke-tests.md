# 플로우 스모크 테스트

이 파일은 routing, agent, skill 매핑이 서로 맞물리는지 확인할 때 사용한다.

## 스모크 테스트 표

| 사용자 요청 | 기대 플로우 |
|---|---|
| "프로젝트 구조 설명해줘" | Orchestrator -> `skills/command-routing.md` |
| "세부 로드맵 짜줘" | Research + Integration -> `skills/implementation-planning.md` |
| "워커로 나눠서 작업 폴더 만들어줘" | Orchestrator + Issue Manager -> `skills/task-orchestration.md` |
| "비즈니스 로직 규칙 정리해줘" | Orchestrator + Structure Manager -> `rules/README.md` -> `rules/business-logic.md` |
| "artifact 저장 정책 확인해줘" | Evaluation + Structure Manager -> `rules/data-and-artifacts.md` |
| "완료 기준과 검증 규칙 확인해줘" | Review Orchestrator -> `rules/review-and-verification.md` |
| "모듈 경계 규칙 확인해줘" | Structure Manager -> `rules/architecture-boundaries.md` |
| "촬영 프로토콜 잡아줘" | Data and Capture -> `skills/capture-protocol.md` |
| "SAM2 tracking adapter 만들어줘" | Issue Manager -> Git Manager -> Segmentation -> Review |
| "Depth/pose가 이상해" | Geometry -> `skills/geometry-validation.md` -> 필요 시 Failure Recorder |
| "masked point cloud fusion 구현" | Reconstruction + Geometry 지원 -> Review |
| "bbox와 크기 측정 구현" | Object Prior + Segmentation/Geometry 입력 -> Evaluation -> Review |
| "실험 결과 기록해줘" | Evaluation -> `skills/experiment-logging.md` |
| "데모 화면 만들어줘" | Visualization -> `skills/visual-demo.md` |
| "PR 리뷰해줘" | Review Orchestrator -> `skills/code-review-stack.md` -> `skills/pr-review-commenting.md` |
| "PR 충돌 정리해줘" | PR Merge Orchestrator -> `skills/pr-merge-orchestration.md` -> 필요 시 `skills/decision-brief.md` |
| "이 실패 기록해줘" | Failure Recorder -> `skills/failure-recording.md` |

## 통과 기준

- 각 flow에는 primary owner가 하나만 있다.
- 구현 flow는 Issue/worktree 계획에서 시작한다.
- `PR 충돌`처럼 키워드가 겹치는 요청은 conflict/decision 흐름을 우선한다.
- multi-worker flow는 `.claude/tasks/<task-name>/`을 만든다.
- review flow는 PR에 올릴 수 있는 한글 comment를 만든다.
- conflict flow는 사용자 결정 지점에서 멈춘다.

## 목표가 아닌 것

- 이 파일은 실제 테스트를 대체하지 않는다.
- 이 파일은 실행 승인을 의미하지 않는다.
- 이 파일은 merge conflict 결론을 대신 내리지 않는다.
