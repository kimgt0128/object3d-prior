# git.md — git/GitHub 규약

git·GitHub 작업의 규약. GitHub에 보이는 텍스트(커밋·PR·리뷰·이슈)는 한글로 쓴다. 기술 식별자(branch·path·command·model·issue 참조)는 원문 유지.

## 커밋 메시지

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

- `#issue`는 관련 이슈가 있을 때만 붙인다.
- 마지막 줄에 항상: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- 허용 type: `feat` `fix` `docs` `test` `refactor` `perf` `chore` `build`

## 브랜치 이름

`<type>/<issue>-<짧은-설명>` (이슈 없으면 `<type>/<짧은-설명>`). 예: `feat/12-object-prior`, `chore/git-command`.

## 이슈 제목

prefix 없는 평문 한글. `[Feat]` 같은 type prefix를 붙이지 않는다.

## PR 제목

`[Type/<issue>-<branch>]: 한글 요약`. 이 형식은 PR 제목에만 쓰고 이슈 제목에는 쓰지 않는다.

## PR 본문

한글로: 요약 / 변경 내용 / 검증 / 관련 이슈 / 리뷰 포인트 / 한계·후속. 이슈를 완전히 닫으면 `Closes #N`, 일부면 `Related #N`.

## 기본 원칙

- 커밋·푸시는 사용자가 요청할 때만. `main`에서 작업 시작 시 브랜치를 먼저 만든다.
- 관련 없는 파일을 함께 staging하지 않는다.
- raw video·dataset·checkpoint·cache·secret·큰 산출물을 커밋하지 않는다.
- destructive git 작업은 사용자 승인 후에만.
- 검증(테스트·시각 확인) 없이 기능 커밋을 만들지 않는다.

규약이 길어지면 상세를 `.claude/rules/ref/`로 옮기고 이 파일은 짧게 유지한다.
