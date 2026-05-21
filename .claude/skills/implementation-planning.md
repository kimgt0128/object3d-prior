# Implementation Planning 스킬

## 목적

넓은 프로젝트 방향을 agent에게 배정 가능한 phase 단위 작업으로 줄인다.

## 사용할 때

- 사용자가 계획, 로드맵, milestone, 실행 전략을 요청한다.
- 계획이 여러 agent 또는 module에 영향을 준다.
- 구현 전 Issue/worktree 순서가 필요하다.

## 사용하지 않을 때

- 사용자가 작은 직접 수정을 요청했다.
- 특정 Issue가 이미 범위를 정의했다.
- git, review, failure logging만 묻는 요청이다.

## 절차

1. `plans/implementation-strategy.md`에서 시작한다.
2. 다음으로 가장 작고 가치 있는 milestone을 찾는다.
3. 최종 artifact owner를 하나 정한다.
4. distinct output을 소유할 때만 supporting agent를 추가한다.
5. 구현 작업을 Issue-sized slice로 나눈다.
6. 코드 배정 전에 verification을 정의한다.
7. 설명이 길어지거나 작업자가 그대로 따라야 하는 계획이면 `plans/ref/README.md`를 읽고 상세 계획 문서를 만든다.

## 상세 계획 규칙

상세 계획은 Superpowers `using-superpowers`와 `writing-plans` 원칙을 따른다.

- 관련 skill을 먼저 확인한다.
- 실행자가 프로젝트 맥락을 몰라도 이해할 수 있게 파일, 입력, 출력, 검증을 명시한다.
- task는 checkbox로 추적 가능하게 쪼갠다.
- `TBD`, `TODO`, “나중에 구현” 같은 placeholder를 쓰지 않는다.
- 코드 구현 계획이면 test 또는 visual verification 명령을 포함한다.
- 상세 문서는 `.claude/plans/ref/YYYY-MM-DD-<topic>.md`에 저장한다.

## 출력

```text
마일스톤:
주 담당:
지원 agent:
Issue slice:
검증:
위험:
시작하지 말 것:
상세 계획 문서:
```
