# Folder Structure Management 스킬

## 목적

초기 코드가 과하게 구조화되지 않으면서도 다음 agent가 이해하기 쉬운 repository layout을 유지한다.

## 사용할 때

repository structure를 바꾸거나, 새 module을 추가하거나, 파일 위치를 결정할 때 사용한다.

## 사용하지 않을 때

- 기존 module 내부 수정이고 ownership에 영향이 없다.
- 사용자가 구조가 아니라 model behavior 또는 수학을 묻는다.
- 생성 데이터나 큰 artifact를 source folder에 숨기는 이동이다.

## 원칙

- source code는 `src/` 아래에 둔다.
- 실행 가능한 user-facing demo는 `apps/` 아래에 둔다.
- 반복 실행 command는 `scripts/` 아래에 둔다.
- raw data는 `data/raw/` 아래에 둔다.
- generated intermediate file은 `data/interim/` 아래에 둔다.
- processed output은 `data/processed/` 아래에 둔다.
- final report와 visualization은 `data/results/` 아래에 둔다.
- planning과 agent coordination 문서는 `.claude/` 아래에 둔다.
- 반복 적용되는 판단 기준은 `.claude/rules/` 아래에 둔다.
- 큰 model checkpoint는 명시적으로 필요하지 않으면 git 밖에 둔다.

## 향후 layout 후보

구체적인 module boundary가 필요할 때만 `.claude/rules/ref/future-code-layout.md`를 연다.
반복 적용되는 아키텍처 규칙은 `.claude/rules/architecture-boundaries.md`를 우선한다.

```text
configs/
data/
src/object3d/
apps/
scripts/
tests/
docs/
.claude/
```

## 변경 체크리스트

- 새 폴더의 owner가 명확한가?
- source, generated data, docs, external artifact 중 무엇인가?
- `PROJECT.md` 갱신이 필요한가?
- `agents/routing/command-router.md` 갱신이 필요한가?
- commit rule에 영향이 있는가?

## 절차

1. 각 파일을 source, app, script, data, docs, project coordination, external artifact로 분류한다.
2. generated data를 source folder 밖에 둔다.
3. ownership이 바뀌면 routing과 entrypoint 문서를 갱신한다.
4. 두 layout 사이에 의미 있는 trade-off가 있으면 decision brief를 요청한다.

## 출력

```text
제안 위치:
owner:
영향 파일:
갱신할 문서:
위험:
커밋 범위:
```
