# 에이전트

이 폴더는 LLM 세션이 사용하는 에이전트 시스템 전체를 정의한다. 메인 세션이 Orchestrator 역할을 맡아 요청을 분류하고, 역할(role)에 라우팅하며, 멀티에이전트 작업을 조율한다.

프로젝트는 모델 이름이 아니라 책임 단위로 나눈다. 각 역할은 파이프라인의 좁은 영역을 소유하고 다음 역할이 사용할 명확한 산출물을 남긴다.

## 폴더 구성

- `roles/`: 11개 도메인 역할 정의 — issue-manager, git-manager, data-capture, segmentation, geometry, reconstruction, object-prior, evaluation, visualization, structure-manager, integration
- `routing/`: 요청을 역할로 연결하는 라우팅 문서 — command-router, assignment-matrix, routing-tree, routing-patterns, flow-smoke-tests
- `coordination/`: 멀티에이전트 조율 규칙 — orchestrator-rules, approval-policy, handoff-format, multi-agent-workflow, context-memory, context-management
- `templates/`: task, context, log, worker brief/result 템플릿
- `ref/`: 길어진 상세 문서 — pr-orchestration, recommended-workflow-resources
- `learnings.md`: 재사용 가능한 운영 교훈 (append-only)

## 에이전트 종류

- **메인 세션 = Orchestrator**: 라우팅과 synthesis를 소유한다. `coordination/orchestrator-rules.md`를 따른다.
- **네이티브 서브에이전트** (`.claude/agents/`): Claude Code가 `description` 기반으로 자동 인식하고 Task 도구로 dispatch한다.
  - `review-orchestrator`: 계층형 코드·문서 리뷰, PR review comment
  - `failure-recorder`: 실패·삽질을 재사용 가능한 기록으로 저장
  - `researcher`: 논문·도구 조사와 MVP 범위 축소
  - `pr-merge-orchestrator`: 열린 PR 비교와 안전한 병합 전략
- **도메인 역할** (`roles/`): 메인 세션이 직접 읽고 수행하거나, sub-agent 실행이 가능하면 worker brief로 dispatch한다.

서브에이전트가 기대대로 자동 발동하지 않으면 `.claude/agents/`의 해당 파일 `description`을 더 명확히 다듬는다.

## 라우팅 진입

요청은 `routing/command-router.md`로 분류한다. 흐름별 배정은 `routing/assignment-matrix.md`, 짧은 decision tree는 `routing/routing-tree.md`를 참고한다.

## 공통 계약

모든 역할은 작업을 마칠 때 `coordination/handoff-format.md`의 공통 인계 블록을 남긴다. 역할별 산출물 항목은 각 역할 문서가 정의한다. 다른 역할의 출력 형식을 조용히 바꾸지 않는다.

## 하지 말 것

- 라우팅 전에 모든 역할 파일을 읽지 않는다.
- 같은 artifact에 두 primary owner를 배정하지 않는다.
- domain 역할이 git history를 직접 바꾸게 하지 않는다.
- review finding이 결정 없이 사라지게 하지 않는다.
- debugging path가 non-obvious였다면 failure note를 생략하지 않는다.
- Issue 또는 issue draft 없이 기능 구현을 시작하지 않는다.
- 독립 기능 작업에서 두 역할이 하나의 worktree를 공유하게 하지 않는다.
- 사용자 판단이 필요한 conflict를 PR Merge Orchestrator가 자동 병합하게 하지 않는다.

## 커밋과 리뷰 의무

각 역할은 자신의 coherent slice에 대한 커밋 후보와 검증 근거를 남긴다. 실제 staging, commit, PR 문구 정리는 Git Manager가 소유한다. handoff 전:

1. 관련 local verification을 실행한다.
2. 문제를 발견하거나 해결했다면 failure note를 갱신한다.
3. 커밋 후보 경계는 `skills/commit-protocol.md`를 따른다.
4. 리뷰 깊이는 `skills/code-review-stack.md`를 따른다.

중요한 코드는 구현에서 바로 최종 demo로 가지 않는다. `rules/review-and-verification.md`의 계층형 리뷰를 거친다.

## Issue와 worktree 의무

구현 작업 순서:

1. Orchestrator가 `.claude/tasks/<task-name>/`을 만들거나 갱신한다.
2. Issue Manager가 Issue를 만들거나 선택한다.
3. Git Manager가 isolated worktree를 만든다.
4. domain 역할은 해당 worktree 안에서만 작업한다.
5. domain 역할은 `workers/<role>/result.md`를 작성한다.
6. PR이 있으면 Review Orchestrator가 review finding을 PR에 남긴다.
7. PR Merge Orchestrator가 병합 순서를 제안하고 conflict를 사용자에게 올린다.

## task folder 의무

멀티에이전트 작업에서는 chat history를 공유 memory로 사용하지 않는다. 각 worker는 `.claude/tasks/<task-name>/workers/<role>/brief.md`(write scope, expected output, verification 포함)를 받고, `result.md`(읽은·변경 파일, 검증, 다음 owner)를 반환한다. brief 없이 worker를 dispatch하지 않는다.
