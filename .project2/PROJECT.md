# PROJECT.md — 작업 진입점

이 파일은 이 저장소에서 작업을 시작할 때 가장 먼저 읽는 진입점이다. 짧게 유지한다.

## 정체성

이 프로젝트는 SAM 계열 모델의 2D 객체 mask를 depth·camera pose·point cloud와 결합해 3D object prior(추적·크기·방향·confidence·배치 판단)로 승격하는 컴퓨터 비전 프로젝트다.

프로젝트의 목적·범위·MVP·파이프라인(T1~T8)·구현 상태는 `docs/README.md`가 단일 출처다. 작업 전 그 문서를 읽는다.

## 작업 전

`docs/README.md`를 읽고 다음을 정한다 (그 문서의 "Claude/Codex 에이전트 작업 원칙" 체크리스트를 따른다).

1. 지금 목표가 무엇인가?
2. 어느 단계(T1~T8)에 해당하는가?
3. 수정 가능한 파일 범위는 어디인가?
4. 이번 작업에서 하지 않을 것은 무엇인가?
5. 어떻게 검증할 것인가?

## 프로세스는 superpowers에 위임한다

창작·구현·디버깅·리뷰 작업은 설치된 superpowers 스킬을 그대로 쓴다. 하네스는 이 프로세스를 재발명하지 않는다.

- 새 기능·설계: `brainstorming` → `writing-plans`
- 구현: `test-driven-development`
- 버그: `systematic-debugging`
- 완료 주장 전: `verification-before-completion`
- 리뷰: `requesting-code-review` / `receiving-code-review`

## 하지 말 것

- 방 전체 3D 복원부터 시작하지 않는다. 첫 목표는 단일 객체다.
- 문서·폴더 구조를 먼저 키우고 구현이 따라오게 하지 않는다.
- raw video, dataset 원본, model checkpoint, 큰 산출물을 git에 넣지 않는다.
- 실패 frame을 숨기고 성공 frame만 보여주지 않는다.
- 수동 실측값 없이 정확도를 주장하지 않는다.
- 하네스 자동화를 미리 깔지 않는다 (아래 성장 규칙 참고).

## 하네스 성장 규칙

`agents/`, `skills/`, `mcp/`는 비어 있다. 의도된 상태다.

반복되는 고통이 실제로 확인됐을 때만, 항목 하나를 사용자 승인을 받아 추가한다. 미리 만들지 않는다. 각 폴더의 `README.md`에 추가 조건이 있다.

## 현재 초점

T1 capture 안정화. (`docs/README.md`의 "다음에 할 일" 참고.)

- 사용자가 실행할 수 있는 최소 CLI 또는 `main.py` 진입점
- non-integer FPS sampling 처리
- unknown frame count 처리

진행 추적은 git branch와 PR로 한다. 별도 issue/task 폴더는 두지 않는다.

## 참고

`.claude/`는 이전 하네스다. 새 작업에서 읽지 않는다. 이 `.project2/`가 검증된 뒤 `.claude/`를 대체할 예정이다.
