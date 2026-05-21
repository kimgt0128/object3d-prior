# 컨텍스트 관리와 하네스 엔지니어링

이 프로젝트는 progressive disclosure를 따른다. 즉, 현재 명령에 필요한 최소 문서만 읽고, 세부 문서는 트리거가 있을 때만 연다.

## 최초 진입 계약

새 세션은 항상 아래 두 파일에서 시작한다.

```text
.claude/PROJECT.md
.claude/agents/routing/command-router.md
```

그 다음에는 선택된 agent와 skill 파일만 추가로 읽는다.

## 통째로 읽지 말 것

아래 폴더 전체를 한 번에 읽지 않는다.

- `.claude/agents/`
- `.claude/skills/`
- 각 영역의 `ref/` 폴더
- `cv_tutorial/`
- `reference/`

먼저 `rg`, 파일명, 인덱스 문서, command router로 범위를 좁힌다.

## 문서 크기 예산

아래 기준은 강제 규칙이 아니라 유지보수용 권장선이다.

- 진입 파일: 150줄 이하
- router/index 파일: 160줄 이하
- agent 파일: 80줄 이하
- skill 파일: 100줄 이하
- 상세 reference 파일: 길어도 되지만 필요할 때만 읽는다

파일이 예산을 넘기면 예시, 긴 checklist, 배경 설명을 해당 영역의 `ref/` 폴더로 옮기고 원래 파일은 인덱스로 유지한다.

## 파일 역할 규칙

- `PROJECT.md`: 프로젝트 정체성, 목표, 위험, 첫 진입 정책
- `CLAUDE.md` (repository root): Claude Code 세션 자동 로드 진입점
- `agents/routing/*.md`: 명령 분류와 역할 라우팅
- `agents/roles/*.md`: 도메인 역할의 소유권과 산출물 계약
- `agents/coordination/*.md`: 멀티에이전트 조율, 승인 정책, 인계 형식, context/memory 정책
- `agents/templates/*.md`: task와 worker 템플릿
- `.claude/agents/*.md`: Claude Code 네이티브 서브에이전트 정의
- `skills/*.md`: 반복 가능한 실행 절차
- `rules/*.md`: 반복 적용되는 canonical 판단 기준
- `*/ref/*.md`: 긴 checklist, 예시, 상세 설명
- `failures/*.md`: 구체적인 실패 시도와 해결 기록

## 프롬프트 위생

- 긴 긍정 지시보다 anti-pattern과 중단 조건을 우선 기록한다.
- 반복 규칙은 한 곳에만 두고 링크한다.
- 같은 긴 checklist를 여러 파일에 복사하지 않는다.
- 모호한 참조보다 정확한 파일 경로를 쓴다.
- 좁은 명령은 좁은 문서만 읽고 답한다.

## 메모리 위생

- 긴 작업의 유일한 기억 저장소로 채팅 기록만 사용하지 않는다.
- handoff와 artifact index는 현재 `.claude/tasks/<task-name>/` 아래에 저장한다.
- 활성 context는 현재 issue, 선택된 agent, 선택된 skill, 최신 handoff로 제한한다.
- 파일 경로, 결정, 오류, 다음 담당자는 구조화된 형태로 남긴다.
- 활성 오류, 미해결 결정, 변경 파일 목록을 요약 과정에서 지우지 않는다.

## 확장 규칙

아래 상황에서만 더 많은 context를 연다.

- 현재 명령을 분류할 수 없다.
- 선택된 agent가 명시적인 의존 문서를 요구한다.
- 구현 결정이 여러 모듈을 건드린다.
- failure note가 과거 해결 사례를 가리킨다.
- review finding에 코드나 문서 근거가 필요하다.

상세한 context-memory 정책이 필요하면 [context-memory.md](context-memory.md)를 연다.
