# Git Management 스킬

## 목적

branch, commit, staged file을 안전하고 읽기 쉽게 관리한다.

## 사용할 때

git, branch, commit, stacked branch, PR, history cleanup 요청이 있을 때 사용한다.

## 사용하지 않을 때

- 사용자가 git 작업 없이 코드 구현만 요청했다.
- review 또는 verification이 아직 끝나지 않았다.
- destructive command가 필요하지만 사용자가 명시적으로 요청하지 않았다.

## 절차

1. `rules/ref/commit-pr-format.md`를 읽는다.
2. working tree를 확인한다.
3. unrelated file group을 분리한다.
4. raw video, checkpoint, secret, cache가 staged되지 않았는지 확인한다.
5. branch 또는 stacked branch layout을 제안한다.
6. `rules/ref/commit-pr-format.md`의 한글 commit/PR 형식을 사용한다.
7. commit 후 hash와 남은 상태를 보고한다.

## 브랜치 이름

```text
feat/<short-feature>
fix/<short-problem>
docs/<short-doc-topic>
chore/<maintenance-topic>
```

stack 예시:

```text
feat/frame-extraction
feat/sam2-tracking
feat/object-cloud
feat/object-measurement
```

## 안전 규칙

- 명시적 사용자 지시 없이 reset, checkout overwrite, branch deletion을 하지 않는다.
- 특정 파일만 staging하는 방식을 우선한다.
- 아주 작은 fixture가 아니라면 generated data를 커밋하지 않는다.
- GitHub commit message, PR title, PR body, review comment는 한글로 작성한다.

## 출력

```text
현재 branch:
worktree:
변경 파일:
안전한 작업:
차단된 작업:
다음 담당:
```
