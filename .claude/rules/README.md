# 프로젝트 규칙

이 폴더는 에이전트가 작업 중 항상 지켜야 하는 규칙을 담는다.

`plans/`는 실행 계획, 각 영역의 `ref/`는 상세 설명, `rules/`는 반복해서 적용되는 판단 기준이다. 같은 규칙이 여러 문서에 보이면 이 폴더의 문서를 canonical source로 본다.

## 경로 기준

이 폴더의 문서에서 `agents/...`, `skills/...`, `rules/...`, `plans/...`처럼 쓰인 경로는 `.claude/` 내부 상대 경로다.

repository root에서 쉘 명령으로 열 때는 `.claude/` prefix를 붙인다.

## 언제 읽을까

- 구현, 리뷰, 커밋, PR, 병합을 시작하기 전
- 비즈니스 로직이나 MVP 범위가 헷갈릴 때
- git에 올려도 되는 파일과 안 되는 파일을 판단할 때
- agent가 어떤 결정을 직접 내려도 되는지 판단할 때

## 규칙 파일

- `git.md`: git, commit, PR, branch, worktree 규칙
- `business-logic.md`: 프로젝트 제품/도메인/MVP 판단 규칙
- `agent-operation.md`: 에이전트 운영, 스킬, 충돌 처리 규칙
- `context-routing.md`: context loading, router, handoff 규칙
- `data-and-artifacts.md`: 데이터, 모델 산출물, 실험 artifact 규칙
- `review-and-verification.md`: 리뷰, 검증, 완료 주장 규칙
- `architecture-boundaries.md`: 코드 구조, 모듈 경계, source layout 규칙
- `ref/`: 긴 상세 문서 (commit/PR 형식, 계층 리뷰, 리뷰 lens, 코드 layout)

## 하지 말 것

- 긴 구현 설명을 이 폴더에 넣지 않는다. 상세 구현은 `.claude/plans/ref/`나 영역별 `ref/`로 보낸다.
- 특정 실험 결과를 이 폴더에 넣지 않는다. 실험 결과는 task artifact 또는 evaluation log에 둔다.
- 실패 사례를 일반 규칙처럼 뭉개지 않는다. 실패는 `.claude/failures/`에 남긴다.
