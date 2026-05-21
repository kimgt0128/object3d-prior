# 세부 Multi-Agent PR 오케스트레이션

이 파일은 실제 Issue, worktree, PR, review, merge conflict를 조율할 때만 연다.

## 참고 원칙

- Git worktree는 같은 repository에 연결된 독립 작업 트리를 제공한다.
- GitHub Issue는 작업 계약을 추적한다.
- GitHub PR은 토론, 리뷰, 병합 흐름을 제공한다.
- stacked PR은 변경을 작고 리뷰 가능하게 유지한다.
- 코드 리뷰는 완벽주의가 아니라 코드 건강성을 높이는 과정이다.
- 파일 기반 handoff는 supervisor context가 병목이 되는 것을 막는다.

## Task-First와 Issue-First 계약

multi-agent 구현에서는 worker를 보내기 전에 task folder를 만든다.

```text
.claude/tasks/<task-name>/
  task.md
  context.md
  log.md
  workers/<role>/brief.md
  workers/<role>/result.md
```

task folder는 coordination state를 저장한다. Issue는 실제 작업 계약을 저장한다.

## Issue-First 계약

각 agent는 하나의 Issue에서 시작한다.

GitHub를 사용할 수 있으면:

```text
gh issue create --title "<title>" --body-file <body.md>
```

GitHub를 사용할 수 없으면:

```text
.claude/issues/YYYY-MM-DD-<slug>.md
```

Issue 본문은 한글로 작성하고 아래 항목을 포함한다.

```markdown
# Issue: <제목>

## 목표

## 담당

## 범위

## 하지 않을 일

## 입력

## 기대 산출물

## 수정 허용 파일

## 수정 금지 파일

## 검증

## 충돌 위험
```

## Worktree 계약

각 Issue는 자기 branch와 worktree를 가진다.

Branch 이름:

```text
agent/<issue-number-or-slug>/<short-topic>
```

Worktree 경로:

```text
.worktrees/<branch-slug>/
```

아래 조건이 맞기 전에는 worktree를 만들지 않는다.

- git repository가 있다.
- `.worktrees/`가 ignore되어 있다.
- branch name이 고유하다.
- Issue scope가 명확하다.

orchestrator가 integration task로 선언하지 않은 한, 두 agent가 같은 파일을 수정하지 않게 한다.

각 Issue는 task coordination folder를 링크한다.

```text
.claude/tasks/<task-name>/
```

최소한 `task.md`, `context.md`, `log.md`, worker result는 최신 상태를 유지한다. 큰 log나 raw model output을 PR description에 붙이지 않는다.

## PR 계약

완료된 worktree는 Issue에 연결된 PR 하나를 연다.

PR 제목 형식:

```text
[Type/<issue>-<branch>]: 한글 요약
```

예시:

```text
[Fix/3-login]: 전체적인 로그인 로직 수정
[Feat/12-object-prior]: 객체 크기 측정 파이프라인 추가
```

PR 본문은 한글로 작성하고 아래 항목을 포함한다.

```markdown
## 요약

## 변경 내용

## 검증

## 관련 이슈

Closes #<issue-number>

## 작업 에이전트

## 작업 폴더

## 시각 자료

## 리뷰 포인트

## 한계 및 후속 작업

## 병합 참고 사항
```

부분 작업 PR이라 Issue를 닫으면 안 되는 경우 `Closes` 대신 일반 참조만 사용한다.

## 리뷰 댓글 계약

PR이 있으면 리뷰 결과는 PR comment로 남긴다.

일반 PR review comment 권장 명령:

```text
gh pr review <number-or-url> --comment --body-file <review.md>
```

inline review comment는 특정 diff line에 정확히 묶을 수 있을 때만 사용한다.

리뷰 comment template은 한글로 작성한다.

```markdown
## 자동 리뷰 요약

### 적용한 리뷰 계층
- 스펙 준수:
- 검증 근거:
- 도메인 리뷰:
- 통합 영향:

### 발견 사항

#### 차단 이슈

#### 수정 권장

#### 선택 사항

### 병합 전 필요 작업

### 오케스트레이터 참고 사항
```

사용자가 명시적으로 승인하지 않은 한 자동으로 approve 또는 request changes를 하지 않는다.

## 병합 오케스트레이션

PR Merge Orchestrator는 기본적으로 직접 merge하지 않는다. 먼저 전략을 제안한다.

확인 항목:

- 연결된 Issue
- branch base
- 수정 파일
- 계약 변경
- test status
- visual evidence
- review finding
- conflict risk
- 다른 PR 의존성
- `.claude/tasks/<task>/workers/<role>/result.md`
- `.claude/tasks/<task>/artifacts/`

병합 전략 후보:

1. 독립 PR은 review 통과 후 순서와 무관하게 merge한다.
2. stacked PR은 base에서 top 순서로 merge한다.
3. 의존 PR은 parent merge 후 rebase한다.
4. review 범위가 너무 넓으면 PR split을 요청한다.
5. 충돌 PR은 사용자 decision brief로 전환한다.

## 충돌 분류

| 충돌 | Orchestrator 조치 |
|---|---|
| 같은 파일, 겹치지 않는 문서 수정 | review 후 manual 또는 auto merge 제안 |
| 같은 output contract | decision brief로 escalation |
| 같은 model adapter interface | decision brief로 escalation |
| 서로 다른 folder structure 제안 | decision brief로 escalation |
| reviewer가 severity에 disagree | evidence를 요약하고 사용자에게 질문 |
| 한 PR이 다른 PR을 무효화 | merge order 또는 replacement 제안 |
| 단순 git conflict | 더 낮은 위험 branch에서 rebase/merge fix 제안 |

agent 간 correctness conflict를 다수결로 해결하지 않는다. evidence, reviewer confidence, 사용자 decision brief를 사용한다.

## 사용자 결정 brief

escalation이 필요하면 아래 형식으로 제시한다.

```markdown
## 결정 필요

### 충돌

### 선택지 A
- 장점:
- 비용:
- 위험:
- 되돌리기 가능 여부:

### 선택지 B
- 장점:
- 비용:
- 위험:
- 되돌리기 가능 여부:

### 추천

### 선택 후 수행할 일
```

사용자가 선택하기 전에는 병합을 계속하지 않는다.
