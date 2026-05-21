# Issue Worktree Workflow 스킬

## 목적

각 agent가 명확한 Issue와 isolated worktree에서 작업하도록 보장한다.

## 사용할 때

- 기능, 버그, 실험, 리뷰 수정, 문서 작업을 agent에게 배정한다.
- 계획에서 구현을 시작한다.
- 여러 agent로 작업을 나눈다.

## 사용하지 않을 때

- 논의만 하는 작업이다.
- 현재 디렉터리가 git repository가 아니고 사용자가 계획만 원한다.
- 공유 planning folder의 아주 작은 문서 수정이다.

## 절차

1. `PROJECT.md`와 `agents/routing/command-router.md`를 읽는다.
2. 멀티에이전트 구현이면 task folder가 있는지 확인한다.
3. Issue를 만들거나 선택한다.
4. owner, scope, non-goal, allowed file, verification을 정의한다.
5. 해당 Issue용 branch와 isolated worktree를 만든다.
6. worktree 경로와 Issue contract를 assigned agent에게 넘긴다.
7. commit은 `rules/ref/commit-pr-format.md`를 따르게 한다.
8. Issue와 연결된 PR을 열거나 준비한다.

## 출력

```text
Issue:
작업 폴더:
담당:
branch:
worktree:
허용 파일:
검증:
PR 대상:
충돌 위험:
```
