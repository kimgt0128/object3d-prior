# 명령 라우터

이 파일은 사용자 요청을 적절한 에이전트, 스킬, 리뷰 깊이로 연결한다.

## 필수 진입 흐름

새 에이전트 세션은 다음 순서로 시작한다.

```text
1. .claude/PROJECT.md 읽기
2. .claude/agents/routing/command-router.md 읽기
3. 사용자 요청 분류
4. 매칭되는 역할 문서(.claude/agents/roles/) 또는 네이티브 서브에이전트(.claude/agents/)만 읽기
5. .claude/skills/에서 매칭되는 skill 파일만 읽기
6. 멀티에이전트 작업이면 .claude/tasks/ 아래 task folder 생성 또는 갱신
7. 해당 역할의 소유 범위 안에서만 실행 또는 계획
8. 필요하면 failure note, review note, commit guidance 갱신
```

모든 agent, skill, reference를 읽지 않는다. 선택된 owner가 진행할 수 없을 때만 컨텍스트를 확장한다.

## 경로 기준

이 파일 안의 `agents/...`, `skills/...`, `rules/...`, `plans/...` 경로는 모두 `.claude/` 폴더 기준이다. 긴 상세는 각 영역의 `ref/`에 있다.

터미널 CWD가 repository root이면 실제 파일은 `.claude/agents/...`처럼 연다. 이미 `.claude/...`로 표기된 경로는 repository root 기준이다.

## 오케스트레이션 규칙

sub-agent 실행이 가능하면 write scope가 겹치지 않는 독립 역할만 병렬로 dispatch한다.

sub-agent 실행이 불가능하면 같은 라우팅을 순차적으로 시뮬레이션한다.

```text
orchestrator -> selected domain agent -> selected review agent -> integration handoff
```

이미 존재하는 agent가 소유할 수 있는 요청에 새 역할을 만들지 않는다.

## 명령 분류

## 키워드 우선순위

여러 행에 동시에 걸리는 요청은 아래 우선순위로 분류한다.

1. "충돌", "conflict", "결정 필요"가 있으면 conflict/decision 흐름을 우선한다.
2. "PR", "병합", "merge"가 있으면 PR Merge Orchestrator 흐름을 우선한다.
3. CV 파이프라인이나 소스 코드를 새로 만들거나 고치는 구현 요청이면(예: "기능 구현", "모듈/어댑터/파이프라인 만들어줘", "코드 수정") domain agent에 보내기 전에 Issue/worktree 준비를 먼저 거친다. 커밋·리뷰·병합·계획·문서 정리처럼 파이프라인 코드를 직접 만들지 않는 요청은 "만들어줘" 같은 단어가 있어도 이 규칙 대신 1·2·4순위와 분류표 키워드로 라우팅한다.
4. "리뷰", "review", "gstack"이 있으면 Review Orchestrator 흐름을 우선한다.
5. domain keyword만 있으면 해당 domain agent로 보낸다.
6. 위 우선순위에도 아래 분류표에도 맞지 않으면 추측해서 라우팅하지 않는다. Orchestrator가 사용자에게 의도를 확인하는 질문을 한 뒤 분류한다.

| 사용자 요청 의도 | 주 담당 | 참고 문서 |
|---|---|---|
| "프로젝트 시작", "진입점 확인", "구조 설명", "전체 구조" | Orchestrator Agent | `agents/coordination/orchestrator-rules.md`, `skills/command-routing.md` |
| "계획 짜줘", "세부 전략", "로드맵" | Research Agent + Integration Agent | `.claude/agents/researcher.md`, `agents/roles/integration.md`, `skills/implementation-planning.md`, `plans/implementation-strategy.md` |
| "상세 계획", "세부 설명", "구체적으로", "단계별 실행 계획" | Research Agent + Integration Agent | `skills/implementation-planning.md`, `plans/implementation-strategy.md`, `plans/ref/README.md` |
| "task", "worker", "brief", "작업 폴더", "워커", "작업 분해" | Orchestrator Agent + Issue Manager Agent | `agents/coordination/orchestrator-rules.md`, `agents/roles/issue-manager.md`, `skills/task-orchestration.md`, `agents/templates/task-folder.md` |
| "issue", "이슈", "작업 할당", "agent 할당" | Issue Manager Agent | `agents/roles/issue-manager.md`, `skills/issue-worktree-workflow.md` |
| "worktree", "워크트리", "독립 작업공간" | Git Manager Agent + Issue Manager Agent | `agents/roles/git-manager.md`, `agents/roles/issue-manager.md`, `skills/issue-worktree-workflow.md`, `skills/git-management.md` |
| "PR", "pull request", "병합", "merge order" | PR Merge Orchestrator Agent | `.claude/agents/pr-merge-orchestrator.md`, `skills/pr-merge-orchestration.md` |
| "context", "memory", "token", "compaction", "컨텍스트", "메모리", "오케스트레이션 최적화" | Orchestrator Agent + Structure Manager Agent | `skills/context-memory-optimization.md`, `agents/coordination/context-management.md` |
| "rules", "규칙", "비즈니스 로직", "도메인 규칙" | Orchestrator Agent + Structure Manager Agent | `rules/README.md`, `rules/business-logic.md`, `rules/agent-operation.md` |
| "artifact", "산출물", "데이터 저장", "checkpoint", "raw data" | Evaluation Agent + Structure Manager Agent | `rules/data-and-artifacts.md`, `skills/experiment-logging.md` |
| "검증 규칙", "완료 기준", "review gate", "완료 주장" | Review Orchestrator Agent | `rules/review-and-verification.md`, `rules/ref/review-stack.md` |
| "모듈 경계", "source layout", "패키지 구조", "아키텍처 규칙" | Structure Manager Agent | `rules/architecture-boundaries.md`, `rules/ref/future-code-layout.md` |
| "촬영", "capture", "영상 수집", "데이터 수집", "실측", "ground truth" | Data and Capture Agent | `agents/roles/data-capture.md`, `skills/capture-protocol.md` |
| "SAM", "마스크", "segmentation", "tracking" | Segmentation Agent | `agents/roles/segmentation.md`, `skills/model-adapter.md` |
| "MapAnything", "VGGT", "depth", "pose", "camera" | Geometry Agent | `agents/roles/geometry.md`, `skills/geometry-validation.md` |
| "point cloud", "backprojection", "fusion", "TSDF" | Reconstruction Agent | `agents/roles/reconstruction.md`, `skills/geometry-validation.md` |
| "bbox", "크기 측정", "orientation", "placement" | Object Prior Agent | `agents/roles/object-prior.md`, `skills/object-prior-fitting.md` |
| "성능", "오차", "ablation", "데이터 분석" | Evaluation Agent | `agents/roles/evaluation.md`, `skills/experiment-logging.md` |
| "Rerun", "Open3D", "Gradio", "데모" | Visualization Agent | `agents/roles/visualization.md`, `skills/visual-demo.md` |
| "폴더 구조", "아키텍처 정리", "모듈 분리" | Structure Manager Agent | `agents/roles/structure-manager.md`, `skills/folder-structure-management.md` |
| "git", "branch", "commit", "커밋" | Git Manager Agent | `agents/roles/git-manager.md`, `rules/ref/commit-pr-format.md`, `skills/commit-protocol.md` |
| "코드리뷰", "review", "gstack", "스택 리뷰" | Review Orchestrator Agent | `.claude/agents/review-orchestrator.md`, `rules/ref/review-stack.md`, `skills/code-review-stack.md`, `skills/pr-review-commenting.md` |
| "충돌", "conflict", "의견 갈림", "결정 필요" | Orchestrator Agent + PR Merge Orchestrator Agent | `skills/decision-brief.md`, `agents/ref/pr-orchestration.md` |
| "실패 기록", "안됨", "오류", "삽질 기록" | Failure Recorder Agent + 관련 domain agent | `.claude/agents/failure-recorder.md`, `skills/failure-recording.md`, `failures/README.md` |
| "하지 말아야", "금지", "anti-pattern", "실패 방지" | Orchestrator Agent | `agents/coordination/orchestrator-rules.md`, `skills/anti-pattern-check.md`, `rules/business-logic.md`, `agents/coordination/context-management.md` |

## 멀티에이전트 실행 패턴

구현은 task-first와 Issue-first 흐름을 따른다.

```text
task folder -> issue draft -> worker brief -> isolated worktree -> result -> review -> PR/merge strategy
```

상위 라우팅만으로 부족할 때만 `agents/routing/routing-patterns.md`를 연다.

구현 요청으로 분류된 경우 domain agent가 바로 파일을 수정하지 않는다. 먼저 Issue Manager와 Git Manager가 Issue 또는 issue draft, branch, isolated worktree 가능 여부를 확인한다.

## 라우팅 규칙

- 하나의 요청은 여러 agent와 연결될 수 있지만 최종 산출물 owner는 하나여야 한다.
- 하나의 writable artifact에 여러 primary owner를 배정하지 않는다.
- 분류표에서 "A + B"로 표기된 행은 A가 주 담당(최종 산출물 owner)이고 B는 지원이다. 주/지원 구분은 `agents/routing/assignment-matrix.md`를 따른다.
- 모델 출력과 geometry가 함께 나오면 Geometry Agent가 coordinate contract를 소유한다.
- SAM과 measurement가 함께 나오면 Segmentation Agent는 mask를, Object Prior Agent는 dimension을 소유한다.
- 폴더 구조를 건드리면 Git Manager 커밋 전에 Structure Manager가 검토한다.
- git 관련 요청은 Git Manager가 staging과 commit recommendation을 소유한다.
- review 요청은 Review Orchestrator가 리뷰 형태와 PR comment 출력을 소유한다.
- merge 요청은 PR Merge Orchestrator가 병합 전략을 소유하며 직접 병합하지 않는다.
- 실패한 시도가 드러나면 Failure Recorder가 failure note를 만들거나 갱신한다.
- 구현이 시작되면 Issue Manager가 Issue 또는 issue draft를 보장한다.
- 여러 worker가 필요하면 Orchestrator가 dispatch 전에 task folder를 만들거나 갱신한다.
- PR이 있으면 사용자가 local-only review를 요청하지 않는 한 리뷰 결과를 PR에 남긴다.
- 한 supervisor 아래 active agent를 3-5개 이상 두지 않는다. 필요하면 조율 단위를 쪼갠다.
- scoped instruction과 file handoff로 충분하면 전체 프로젝트 컨텍스트를 넘기지 않는다.
- 큰 결과는 채팅에 붙이지 말고 활성 task folder에 저장한 뒤 경로만 넘긴다.

## 에이전트 인계 형식

모든 라우팅된 agent는 작업을 마칠 때 `agents/coordination/handoff-format.md`의 공통 인계 블록으로 마무리한다. 역할 문서가 역할별 산출물 항목을 추가로 정의하면, 그 항목을 채운 뒤 공통 인계 블록을 붙인다.

## 기본 리뷰 깊이

- 문서만 변경: self-check + structure review
- 단일 utility: self-check + test
- segmentation/geometry/prior 코드: stacked review
- 여러 모듈을 건드리는 pipeline: stacked review + integration review
- 최종 demo: stacked review + failure log scan + commit check

## 참고 문서 로딩 규칙

- docs, routing, context policy를 바꿀 때만 `agents/coordination/context-management.md`를 연다.
- 반복 적용되는 판단 기준을 확인할 때만 `rules/README.md`와 필요한 rule 파일을 연다.
- phase index만으로 부족할 때만 `plans/ref/implementation-phases.md`를 연다.
- 계획 설명이 길어지거나 checkbox 기반 실행 계획이 필요할 때만 `plans/ref/README.md`와 해당 상세 계획을 연다.
- 실제 source layout을 설계할 때만 `rules/ref/future-code-layout.md`를 연다.
- 모델/논문/개념 설명이 필요할 때만 `plans/ref/model-concept-map.md`를 연다.
- domain review 중에만 `rules/ref/review-lenses.md`를 연다.
- Issue, worktree, PR, conflict 조율이 필요할 때만 `agents/ref/pr-orchestration.md`를 연다.
- context, memory, handoff, multi-agent 최적화가 필요할 때만 `agents/coordination/context-memory.md`를 연다.
- 구체적인 dispatch diagram이 필요할 때만 `agents/routing/routing-patterns.md`를 연다.
- 라우팅 커버리지를 검증할 때만 `agents/routing/assignment-matrix.md` 또는 `agents/routing/flow-smoke-tests.md`를 연다.
- 멀티에이전트 조율이 필요할 때만 `agents/routing/routing-tree.md`, `agents/coordination/approval-policy.md`, `agents/coordination/orchestrator-rules.md`를 연다.
- 구현, 리뷰, git, architecture 작업 전에는 `rules/business-logic.md`를 확인한다.
