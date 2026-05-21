# 에이전트 운영 규칙

이 파일은 Orchestrator와 domain agent가 작업을 나눌 때 지켜야 하는 규칙이다.

## 기본 진입

새 작업은 `.claude/PROJECT.md`와 `.claude/agents/routing/command-router.md`에서 시작한다.

그 다음 필요한 agent, skill, rule만 읽는다. 모든 문서를 한 번에 읽지 않는다.

## Superpowers 규칙

- 관련 Superpowers skill이 1%라도 적용될 가능성이 있으면 먼저 확인한다.
- 계획 작업은 `superpowers:writing-plans` 원칙을 따른다.
- 구현 실행은 필요할 때 `superpowers:using-git-worktrees`, `superpowers:subagent-driven-development`, `superpowers:executing-plans`를 사용한다.
- 완료 주장 전에는 verification 성격의 확인을 한다.
- 코드 리뷰 전후에는 requesting/receiving code review 계열 skill을 확인한다.

## 작업 분해 규칙

- 최종 artifact owner는 하나만 둔다.
- supporting agent는 입력, 검토, 보조 산출물만 소유한다.
- write scope가 겹치면 병렬 작업하지 않는다.
- 구현 요청이면 Issue Manager와 Git Manager를 먼저 거친다.
- 긴 계획은 `.claude/plans/ref/`에 checkbox 기반 상세 계획으로 분리한다.

## 충돌 처리

아래 충돌은 자동으로 결정하지 않는다.

- product scope 변경
- architecture 변경
- model stack 변경
- GPU/data/time 요구사항 증가
- destructive git operation
- 한 PR을 살리기 위해 다른 PR을 버려야 하는 상황

이 경우 `.claude/skills/decision-brief.md` 형식으로 사용자에게 선택지를 제시한다.

## handoff 규칙

모든 agent는 작업을 마칠 때 `agents/coordination/handoff-format.md`의 공통 인계 블록을 남긴다. 그 형식이 canonical이다.

## 멈출 조건

- task folder 없이 여러 agent를 dispatch하려 한다.
- worker brief 없이 구현을 시작하려 한다.
- 같은 파일을 두 agent가 동시에 수정하려 한다.
- 큰 로그나 모델 출력을 채팅에 그대로 붙이려 한다.
- 실패를 기록하지 않고 같은 시도를 반복하려 한다.
