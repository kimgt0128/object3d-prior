# Context와 라우팅 규칙

이 파일은 에이전트가 어떤 문서를 언제 읽고, 어떤 owner에게 넘길지 판단하는 기준이다.

## 최초 진입

- 새 작업은 `.claude/PROJECT.md`와 `.claude/agents/routing/command-router.md`에서 시작한다.
- 그 다음 선택된 agent, skill, rule만 읽는다.
- 모든 agent, skill, reference, task folder를 한 번에 읽지 않는다.

## 경로 해석

- 이 프로젝트 운영 문서의 짧은 경로는 `.claude/` 기준이다.
- 예를 들어 `agents/coordination/orchestrator-rules.md`는 repository root에서 `.claude/agents/coordination/orchestrator-rules.md`로 연다.
- `.claude/...`로 시작하는 경로는 repository root 기준 그대로 연다.
- 경로가 안 열리면 새 파일을 만들기 전에 `rg --files --no-ignore`로 실제 위치를 확인한다.

## Context loading 규칙

- `.claude/agents/` 전체를 읽지 않는다.
- `.claude/skills/` 전체를 읽지 않는다.
- 각 영역의 `ref/` 폴더를 통째로 읽지 않는다.
- `cv_tutorial/`와 `reference/`는 먼저 검색한 뒤 필요한 파일만 연다.
- 좁은 명령은 좁은 문서만 읽고 답한다.
- 큰 출력은 채팅에 붙이지 말고 task artifact로 저장한 뒤 경로를 남긴다.

## Router 규칙

- 최종 artifact owner는 하나만 둔다.
- supporting agent는 입력, 검토, 보조 산출물만 소유한다.
- 구현 요청이면 Issue Manager와 Git Manager를 먼저 거친다.
- 모델 출력과 geometry가 함께 나오면 Geometry Agent가 coordinate contract를 소유한다.
- SAM과 measurement가 함께 나오면 Segmentation Agent는 mask를, Object Prior Agent는 dimension을 소유한다.
- 리뷰 요청은 Review Orchestrator가 소유한다.
- 병합 전략은 PR Merge Orchestrator가 소유한다.

## Handoff 규칙

handoff에는 `agents/coordination/handoff-format.md`의 공통 인계 블록을 남긴다. 그 형식이 canonical이다.

## 멈출 조건

- 현재 명령을 분류할 수 없다.
- write scope가 겹치는데 병렬 작업을 하려 한다.
- worker brief 없이 구현을 시작하려 한다.
- 활성 오류, 미해결 결정, 변경 파일 목록이 요약 과정에서 사라질 위험이 있다.
