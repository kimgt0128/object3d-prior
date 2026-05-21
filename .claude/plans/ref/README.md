# 상세 계획 문서 규칙

이 폴더는 `.claude/plans/implementation-strategy.md`에 모두 넣기에는 길지만, 구현자나 에이전트가 정확히 따라야 하는 상세 계획을 저장한다.

## 사용할 때

- phase index만으로 구현 순서가 부족하다.
- 어떤 파일을 만들고 수정해야 하는지 명확히 적어야 한다.
- test, visual check, expected output이 필요한 작업이다.
- 여러 agent가 같은 목표를 나눠 수행한다.
- 설명이 길어져서 상위 plan의 가독성을 떨어뜨린다.

## 사용하지 않을 때

- 한두 문장 설명이면 `.claude/plans/implementation-strategy.md`에 남긴다.
- 단순 개념 설명이면 `.claude/plans/ref/model-concept-map.md` 또는 별도 reference로 둔다.
- 실패 기록이면 `.claude/failures/`에 남긴다.
- 현재 작업의 상태 공유라면 `.claude/tasks/<task-name>/`에 남긴다.

## Superpowers 적용 규칙

상세 계획을 작성하기 전에는 관련 Superpowers skill을 먼저 확인한다.

- 계획 작성: `superpowers:writing-plans`
- 멀티에이전트 실행: `superpowers:subagent-driven-development`
- plan 실행: `superpowers:executing-plans`
- worktree 기반 작업: `superpowers:using-git-worktrees`
- 코드 리뷰 요청: `superpowers:requesting-code-review`
- 리뷰 피드백 처리: `superpowers:receiving-code-review`

## 파일 이름

```text
.claude/plans/ref/YYYY-MM-DD-<topic>.md
```

예시:

```text
.claude/plans/ref/2026-05-20-sam2-tracking-adapter.md
.claude/plans/ref/2026-05-20-mask-to-object-cloud.md
```

## 상세 계획 템플릿

```markdown
# <기능 이름> 상세 계획

> 에이전트 작업자용: 이 계획은 checkbox 단위로 실행한다. 구현 전 관련 Superpowers skill과 project routing 문서를 확인한다.

**목표:** 한 문장으로 결과를 설명한다.

**아키텍처:** 어떤 입력을 받아 어떤 출력으로 바꾸는지 설명한다.

**기술 스택:** 필요한 library, model, command를 적는다.

## 파일 구조

- 생성:
- 수정:
- 테스트:
- 산출물:

## 사전 조건

- 필요한 입력:
- 필요한 config:
- 필요한 결정:

## 작업 단계

- [ ] Step 1: 수행할 일
  - 파일:
  - 검증:
  - 기대 결과:

- [ ] Step 2: 수행할 일
  - 파일:
  - 검증:
  - 기대 결과:

## 검증

- unit test:
- smoke test:
- visual check:
- metric:

## 실패 조건

- 어떤 결과가 나오면 멈출지 적는다.
- 실패 기록을 어디에 남길지 적는다.

## 커밋 후보

```text
type(#issue): 한글 요약
```
```

## 작성 금지

- `TBD`
- `TODO`
- “적절히 처리”
- “나중에 구현”
- “비슷하게 반복”
- test 없는 구현 계획
- expected output 없는 실행 명령
