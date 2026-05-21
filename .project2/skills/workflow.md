# Workflow — 표준 작업 흐름

이 프로젝트의 작업 프로세스는 설치된 **superpowers 스킬**을 따른다. 이 문서는
어떤 단계에 어떤 스킬을 쓰는지 정리하고, 프로젝트 고유 절차를 덧붙이는 자리다.

## 단계별 스킬

| 단계 | 스킬 |
|---|---|
| 새 기능·설계 탐색 | `brainstorming` |
| 구현 계획 작성 | `writing-plans` |
| 계획 실행 | `executing-plans` 또는 `subagent-driven-development` |
| 구현 | `test-driven-development` |
| 버그·예상 밖 동작 | `systematic-debugging` |
| 완료 주장 전 | `verification-before-completion` |
| 코드 리뷰 | `requesting-code-review` / `receiving-code-review` |
| 브랜치 마무리 | `finishing-a-development-branch` |

## 서브에이전트 할당

- 메인 세션 = orchestrator. plan·결정·통합·최종 artifact를 소유한다.
- 넓은 탐색 → 빌트인 `Explore`. 설계·계획 → superpowers(메인 세션).
- 독립 구현 task → `implementer`. 변경 리뷰 → `reviewer`.
- 서브에이전트는 결론·handoff만 반환한다. raw 출력을 메인 컨텍스트에 붙이지 않는다.
- 독립 task 2개 이상이면 병렬 dispatch.
- `implementer`·`reviewer`의 커스텀 `.md`는 `agents/`에 두며, 그 역할이 처음
  실제로 필요할 때 하나씩 사용자 승인 후 만든다. 빌트인으로 충분하면 만들지 않는다.

## 확장 방법

- 표준 흐름은 superpowers를 그대로 쓴다. 여기에 중복 작성하지 않는다.
- superpowers가 덮지 못하는 프로젝트 고유 절차가 반복되면, 이 폴더에 md 문서를
  하나 추가한다 (`skills/<name>.md`).
- 그 절차가 Skill 도구로 호출될 만큼 정형화되면 `<name>/SKILL.md` 패키지로
  승격한다. Phase 2에서 `.claude/skills/`로 이동하면 네이티브 Skill로 동작한다.
