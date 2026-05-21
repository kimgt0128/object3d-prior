# 설계: `.project2/` 경량 하네스 재구성

작성일: 2026-05-21

## 배경과 문제

이 저장소는 컴퓨터 비전 프로젝트 **Object3D Prior**다 (프로젝트 상세는 `docs/README.md`).

이전에 `.claude/` 아래에 agents·skills·rules 기반의 큰 하네스를 구성했다. 그 결과 하네스가 실제 프로젝트 코드보다 커졌다 (현재 `.claude/` 88개 파일, 396K, 디렉터리 12개 이상). MVP 도입 단계에서 하네스 자체가 프로젝트를 과도하고 복잡하게 만드는 문제가 확인됐다.

`docs/README.md`의 설계 원칙 5번이 이 문제를 직접 가리킨다: "자동화는 필요해질 때 추가한다. 먼저 no-training MVP를 가볍게 진행하고, 반복되는 고통이 실제로 확인되면 그때 필요한 자동화만 추가한다."

## 목표

`.project2/`에 가볍고 문서 중심인 새 하네스를 짓는다. 검증 후 `.claude/`를 교체한다.

성공 기준:

- 진입점 한 곳(`PROJECT.md`)이 원칙·금지·방향만 담고 한 페이지를 넘지 않는다.
- 프로세스(브레인스토밍·계획·구현·리뷰·검증)는 superpowers 스킬에 위임하고, 하네스가 재발명하지 않는다.
- 자동화(agent·skill·hook·mcp)는 0에서 시작한다. 추가는 항상 사용자 승인을 거친 한 번에 한 항목씩이다.
- 나중에 `.project2/` → `.claude/` rename만으로 Claude Code 네이티브 자동화가 복구되도록 폴더 규격을 맞춘다.

비목표:

- 기존 `.claude/`의 11개 role, rules, 계층 리뷰 문서를 새 구조로 이전하지 않는다. legacy로 둔다.
- issue/task 추적용 폴더를 새로 만들지 않는다. 진행 추적은 git/PR로 한다.
- MCP 서버를 지금 연동하지 않는다.

## 핵심 제약

Claude Code의 자동 인식은 `.claude/`에서만 동작한다. `.claude/agents/`의 서브에이전트 자동 dispatch, `.claude/skills/`의 Skill 호출, `.claude/settings.json`의 hook이 그 대상이다. `.project2/`에 둔 것은 자동 연결되지 않으며, 라우팅 시 수동으로 읽는 일반 마크다운 문서로 동작한다.

따라서 `.project2/` 단계에서 하네스는 **문서 기반**으로 동작한다. 루트 `CLAUDE.md`(Claude Code가 자동 로드하는 유일한 파일)가 `.project2/PROJECT.md`를 진입점으로 가리킨다.

## 파일 구조

```text
CLAUDE.md                  ← 최소 포인터로 재작성 (Claude Code 자동 로드)
.project2/
  PROJECT.md               ← 진입점. 원칙 · 금지 · 방향만
  agents/README.md         ← placeholder
  skills/README.md         ← placeholder
  mcp/README.md            ← placeholder
docs/
  README.md                ← 그대로. 프로젝트 상세의 단일 출처
.claude/                   ← 손대지 않음. 교체 시점까지 legacy로 방치
```

역할 분리:

- `docs/README.md` — 프로젝트가 **무엇인가**. 목적, 범위, MVP, 파이프라인(T1~T8), 구현 상태.
- `.project2/PROJECT.md` — 에이전트가 **어떻게 일하는가**. 진입점, 원칙, 금지, 방향.

PROJECT.md는 프로젝트 내용을 다시 적지 않고 `docs/README.md`를 가리킨다. 같은 규칙을 두 파일에 중복하지 않는다.

## 컴포넌트

### CLAUDE.md (루트, 재작성)

Claude Code가 자동 로드하는 유일한 파일. 최소 포인터로 만든다.

- 한 줄 정체성.
- "작업 전 `.project2/PROJECT.md`를 읽어라."
- 그 외 내용 없음. 현재의 긴 라우팅·역할·규칙 설명은 모두 제거한다.

### .project2/PROJECT.md (진입점)

한 페이지 이내. 다음 섹션만 둔다.

1. **정체성 한 줄** — "SAM mask를 3D object prior로 승격. 프로젝트 상세는 `docs/README.md`."
2. **작업 전** — `docs/README.md`를 읽고 목표 / T1~T8 단계 / 수정 범위 / 안 할 것 / 검증 방법을 정한다. `docs/README.md`의 "Claude/Codex 에이전트 작업 원칙" 체크리스트를 가리키며 복제하지 않는다.
3. **프로세스는 superpowers에 위임** — 창작·구현 작업은 brainstorming → writing-plans → TDD → debugging → code-review → verification 스킬을 그대로 쓴다. 하네스는 이 프로세스를 재발명하지 않는다.
4. **하드 금지** (빠른 가드레일, 5개 안팎):
   - 방 전체 복원부터 시작하지 않는다.
   - 문서·폴더 구조를 먼저 키우고 구현이 따라오게 하지 않는다.
   - raw data, checkpoint, 큰 산출물을 git에 넣지 않는다.
   - 실패 frame을 숨기지 않는다.
   - 하네스 자동화를 미리 깔지 않는다.
5. **하네스 성장 규칙** — agents/·skills/·mcp/는 비어 있다. 반복되는 고통이 실제로 확인되면 항목 **하나**를 사용자 승인 후 추가한다. 미리 만들지 않는다.
6. **현재 초점** — T1 capture 안정화 (CLI 진입점, non-integer FPS, unknown frame count 처리). 진행은 git/PR로 추적하고 별도 issues/tasks 폴더는 두지 않는다.

### placeholder README 3개

각 폴더에 짧은 README를 둔다. 무엇을 두는 곳인지, 언제 추가하는지를 정직하게 적는다.

- `agents/README.md` — Claude Code 네이티브 서브에이전트(`.md` + frontmatter)를 두는 곳. 현재 0개. 같은 종류의 작업을 반복 위임하는 고통이 확인될 때 한 개씩 추가.
- `skills/README.md` — 재사용 가능한 절차 스킬을 두는 곳. 현재 0개. superpowers가 못 덮는 프로젝트 고유 절차가 반복될 때 한 개씩 추가.
- `mcp/README.md` — MCP 서버 설정 관련 메모를 두는 곳. `docs/README.md`에 MCP 필요가 명시된 적 없으므로 현재 확인된 필요 없음. Claude Code의 MCP 설정은 루트 `.mcp.json`이며 이 폴더는 자동 로드되지 않는다는 점을 명시한다. 연동이 필요해지면 그때 추가.

## 전환 계획

### Phase 1 (지금)

1. `.project2/` 생성: `PROJECT.md` + 세 폴더의 `README.md`.
2. 루트 `CLAUDE.md`를 `.project2/PROJECT.md`를 가리키는 최소 포인터로 재작성.
3. `.claude/`는 내용 그대로 둔다. 단 `.claude/settings.json`의 기존 SessionStart/UserPromptSubmit hook이 옛 라우팅 문구를 매 턴 주입해 새 흐름과 충돌하므로, 이 hook을 끄거나 새 진입점을 가리키도록 정리한다. **이 settings.json 변경은 별도 사용자 승인을 받는다.**

### Phase 2 (검증 후, 나중)

1. `docs/README.md`가 프로젝트 핵심을 모두 담고 있는지 확인한다.
2. `.claude/`를 `.claude-legacy/`로 archive (원본 보존, 즉시 삭제하지 않음).
3. `.project2/`를 `.claude/`로 rename한다.
4. `CLAUDE.md` 포인터를 `.claude/PROJECT.md`로 갱신한다.
5. 이 시점부터 agents/skills/settings 네이티브 자동화가 활성화된다 (실제 콘텐츠가 추가됐을 때).

## 검증

- Phase 1 완료 후: 새 세션에서 `CLAUDE.md`가 `.project2/PROJECT.md`로 안내하는지, PROJECT.md가 한 페이지 이내인지, 세 README가 placeholder로 정직하게 쓰였는지 육안 확인.
- 기존 `.claude/`가 변경되지 않았는지 `git status`로 확인 (settings.json 정리는 별도 승인 후).
- 설계 문서와 실제 생성 파일이 일치하는지 확인.

## 위험과 한계

- `.project2/` 단계에서는 네이티브 자동화가 동작하지 않는다. 의도된 절충이며, Phase 2 rename으로 해소된다.
- 기존 `.claude/`의 일부 유용한 규칙이 legacy로 묻힐 수 있다. 필요해지면 그때 한 항목씩 새 구조로 가져온다 (성장 규칙과 동일하게 승인 후).
- Phase 1과 Phase 2 사이 기간에는 `.claude/`와 `.project2/`가 공존한다. CLAUDE.md 포인터가 단일 진입점이므로 혼동은 CLAUDE.md만 정확하면 방지된다.
