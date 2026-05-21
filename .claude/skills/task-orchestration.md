# Task Orchestration 스킬

## 목적

멀티에이전트 작업이 chat history에 의존하지 않도록 task folder와 worker brief를 만든다.

## 사용할 때

- 작업을 여러 agent 또는 worker로 나눠야 한다.
- 서로 다른 domain의 독립 하위 작업이 있다.
- 구현에 Issue, worktree, review, merge 조율이 필요하다.
- worker 시작 전 scoped brief가 필요하다.

## 사용하지 않을 때

- 단일 owner가 바로 끝낼 수 있다.
- 논의만 하는 요청이다.
- write scope를 정의할 정보가 부족하다.

## 절차

1. `agents/templates/task-folder.md`를 기준으로 `.claude/tasks/<task-name>/`을 만든다.
2. `task.md`, `context.md`, `log.md`를 채운다.
3. 승인된 worker마다 `workers/<role>/brief.md`를 만든다.
4. worker끼리 write scope가 겹치지 않는지 확인한다.
5. task를 local issue draft 또는 GitHub Issue와 연결한다.
6. 각 worker가 review 전 `result.md`를 작성하게 한다.

## 출력

```text
작업 폴더:
주 담당:
worker:
생성한 brief:
write scope:
승인 게이트:
다음 dispatch:
```
