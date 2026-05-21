# Git 규칙

이 파일은 git, branch, commit, PR, worktree 판단을 빠르게 확인하기 위한 canonical 규칙이다. commit/PR 텍스트의 상세 형식과 예시는 `rules/ref/commit-pr-format.md`를 따른다.

## 반드시 지킬 것

- GitHub에 보이는 commit, PR, review comment, conflict report는 한글로 작성한다.
- 실제 staging, commit, PR 문구 정리는 Git Manager가 소유한다.
- domain agent는 커밋 후보, 변경 이유, 검증 근거, 알려진 한계를 남긴다.
- 구현 작업은 Issue 또는 issue draft에서 시작한다.
- 독립 기능 작업은 isolated worktree를 사용한다.
- PR이 있으면 review finding은 PR comment로 남긴다.
- 충돌이나 병합 순서는 PR Merge Orchestrator가 전략만 제안하고, 사용자 결정이 필요한 건 사용자에게 올린다.

## git에 올리지 말 것

- `project/`
- `reference/`
- `cv_tutorial/`
- raw video
- dataset 원본
- model checkpoint
- cache
- secret
- 큰 point cloud 또는 mesh 산출물

루트 `.gitignore`가 이 규칙을 반영해야 한다.

## 커밋 형식

```text
type(#issue): 한글 요약

본문:
- 변경 내용:
- 변경 이유:
- 검증:

푸터(선택):
- 관련 이슈:
- 후속 작업:
```

## PR 제목 형식

```text
[Type/<issue>-<branch>]: 한글 요약
```

## 멈출 조건

- 관련 없는 파일이 staged되어 있다.
- `project/`, `reference/`, `cv_tutorial/`이 staged되어 있다.
- 검증 없이 기능 커밋을 만들려고 한다.
- 사용자가 승인하지 않은 destructive git operation이 필요하다.
- PR conflict가 단순 text conflict가 아니라 product, architecture, model-stack 결정을 요구한다.
