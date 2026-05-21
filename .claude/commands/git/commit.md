---
description: 현재 변경을 한글 conventional 형식으로 커밋
argument-hint: [커밋 요약 힌트(선택)]
---

현재 변경을 `.claude/rules/git.md`의 커밋 규약에 따라 커밋한다.

1. `git status`와 `git diff --cached`로 staged 범위를 확인한다. staged된 게 없으면 무엇을 stage할지 사용자에게 확인한다.
2. 관련 없는 파일이 섞여 있으면 사용자에게 알리고 멈춘다.
3. `main` 브랜치면 커밋 전에 작업 브랜치를 먼저 만든다 (`.claude/rules/git.md` 브랜치 규칙).
4. `.claude/rules/git.md` 형식으로 커밋 메시지를 작성한다 — `type(#issue): 한글 요약` + 본문(변경 내용·이유·검증) + `Co-Authored-By` 푸터.
5. 커밋 후 `git log --oneline -1`로 결과를 보고한다.

`$ARGUMENTS`가 있으면 커밋 요약 힌트로 사용한다.
