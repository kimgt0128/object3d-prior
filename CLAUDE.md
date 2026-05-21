# CLAUDE.md

이 저장소는 **객체 인식 3D 공간 보조 프로젝트**다. 최신 SAM 계열 모델의 2D mask를 3D object prior로 승격해 객체 추적·크기 측정·배치 가능성 판단을 수행하는 컴퓨터 비전 시스템을 만든다.

## 작업 전 필수 진입 흐름

모든 작업(질문 포함) 전에 다음을 순서대로 읽고 라우팅한다.

1. `.claude/PROJECT.md` — 프로젝트 정체성, 목표, 위험, 진입 정책
2. `.claude/agents/routing/command-router.md` — 요청을 역할·스킬로 분류하는 라우터

프로젝트 폴더 전체를 한 번에 읽지 않는다. 라우터가 고른 역할 문서와 스킬만 추가로 읽는다. 어느 분류에도 맞지 않으면 추측하지 말고 사용자에게 확인한다.

## 에이전트 모델

- **메인 세션 = Orchestrator**: 요청을 분류하고 역할로 라우팅하며 멀티에이전트 작업을 조율한다. `.claude/agents/coordination/orchestrator-rules.md`를 따른다.
- **네이티브 서브에이전트** (`.claude/agents/`): Claude Code가 `description` 기반으로 자동 인식하고 Task 도구로 dispatch한다.
  - `review-orchestrator` — 코드·문서 리뷰, PR review comment
  - `failure-recorder` — 실패·삽질 기록
  - `researcher` — 논문·도구 조사, MVP 범위 축소
  - `pr-merge-orchestrator` — PR 비교와 병합 전략
- **도메인 역할** (`.claude/agents/roles/`): 컴퓨터 비전 파이프라인 11개 역할 정의.

서브에이전트가 기대대로 자동 발동하지 않으면 `.claude/agents/`의 해당 파일 `description`을 더 명확히 다듬는다.

## 규칙 우선순위

- 반복 적용되는 판단 기준은 `.claude/rules/`가 canonical이다 (git, business-logic, agent-operation, context-routing, data-and-artifacts, review-and-verification, architecture-boundaries).
- 구현·리뷰·커밋 전에 `.claude/rules/business-logic.md`의 안티패턴을 확인한다.
- `project/`, `reference/`, `cv_tutorial/`는 git 추적에서 제외된다 (루트 `.gitignore`).

## 경로 표기

운영 문서의 `agents/...`, `skills/...`, `rules/...` 같은 짧은 경로는 `.claude/` 기준이다. 터미널에서는 `.claude/` prefix를 붙여 연다.
