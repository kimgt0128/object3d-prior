# `.project2/` 경량 하네스 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 하네스가 프로젝트 코드보다 비대해진 문제를 해소하기 위해, `.project2/`에 문서 중심의 경량 진입점을 만들고 루트 `CLAUDE.md`가 그것을 가리키게 한다.

**Architecture:** `.project2/PROJECT.md`가 원칙·금지·방향만 담은 한 페이지 진입점이다. `agents/`·`skills/`·`mcp/`는 README placeholder만 두고 비워 둔다. 프로세스는 superpowers 스킬에 위임한다. 기존 `.claude/`는 손대지 않고 legacy로 둔다 (settings.json 훅 정리만 별도 승인 후 수행).

**Tech Stack:** Markdown 문서, JSON 설정. 코드·테스트 없음.

**참고 문서:** 설계 문서 `docs/superpowers/specs/2026-05-21-project2-harness-design.md`.

**검증 방식:** 이 작업은 코드가 아니라 문서·설정이므로 TDD를 쓰지 않는다. 각 태스크의 검증은 파일 내용 육안 확인과 `git diff`다.

---

### Task 1: `.project2/` 진입점 구조 생성

`.project2/`에 진입점 `PROJECT.md`와 세 폴더의 placeholder README를 만든다. 이 시점에는 루트 `CLAUDE.md`가 아직 `.project2/`를 가리키지 않으므로 새 파일들은 동작에 영향을 주지 않는다 (안전한 inert 상태).

**Files:**
- Create: `.project2/PROJECT.md`
- Create: `.project2/agents/README.md`
- Create: `.project2/skills/README.md`
- Create: `.project2/mcp/README.md`

- [ ] **Step 1: `.project2/PROJECT.md` 생성**

다음 내용 그대로 파일을 만든다.

```markdown
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
```

- [ ] **Step 2: `.project2/agents/README.md` 생성**

다음 내용 그대로 파일을 만든다.

```markdown
# agents/

Claude Code 네이티브 서브에이전트를 두는 곳이다. 각 에이전트는 frontmatter(`name`, `description`)를 가진 단일 `.md` 파일이다.

현재: 0개. 의도된 상태다.

## 추가 조건

같은 종류의 작업을 반복해서 위임하게 되고, 그 위임이 매번 같은 컨텍스트 설명을 필요로 한다는 것이 실제로 확인됐을 때만 추가한다. 추가는 한 번에 하나씩, 사용자 승인을 받는다.

미리 만들지 않는다.

## 참고

이 폴더는 `.project2/`에 있는 동안 자동 인식되지 않는다. `.project2/`가 `.claude/`로 rename된 뒤에만 Claude Code가 서브에이전트로 자동 dispatch한다.
```

- [ ] **Step 3: `.project2/skills/README.md` 생성**

다음 내용 그대로 파일을 만든다.

```markdown
# skills/

재사용 가능한 절차 스킬을 두는 곳이다.

현재: 0개. 의도된 상태다.

## 추가 조건

설치된 superpowers 스킬이 덮지 못하는 이 프로젝트 고유의 절차가 반복해서 필요하다는 것이 실제로 확인됐을 때만 추가한다. 추가는 한 번에 하나씩, 사용자 승인을 받는다.

먼저 superpowers에 같은 일을 하는 스킬이 있는지 확인한다. 있으면 새로 만들지 않는다.

## 참고

이 폴더는 `.project2/`에 있는 동안 Skill 도구로 호출되지 않는다. `.claude/`로 rename된 뒤에만 활성화된다.
```

- [ ] **Step 4: `.project2/mcp/README.md` 생성**

다음 내용 그대로 파일을 만든다.

```markdown
# mcp/

MCP 서버 설정 관련 메모를 두는 곳이다.

현재: 확인된 MCP 필요 없음. `docs/README.md`에 MCP 연동 요구가 명시된 적이 없다.

## 추가 조건

외부 도구를 MCP 서버로 연동할 실제 필요가 확인됐을 때만 내용을 추가한다. 사용자 승인을 받는다.

## 참고

Claude Code의 MCP 설정은 저장소 루트의 `.mcp.json`이다. 이 폴더는 자동 로드되지 않으며 메모·설정 스니펫 보관용이다.
```

- [ ] **Step 5: 생성 결과 검증**

Run: `find .project2 -type f | sort`
Expected 출력 (정확히 이 4줄):

```text
.project2/PROJECT.md
.project2/agents/README.md
.project2/mcp/README.md
.project2/skills/README.md
```

이어서 `.project2/PROJECT.md`를 다시 읽어 한 페이지 이내인지, 6개 본문 섹션(정체성·작업 전·프로세스·하지 말 것·하네스 성장 규칙·현재 초점)과 참고가 모두 있는지 육안 확인한다.

- [ ] **Step 6: 커밋**

`.project2/`의 새 파일만 staging한다 (기존 `.claude/` 변경 등 무관한 파일을 섞지 않는다).

```bash
git add .project2/PROJECT.md .project2/agents/README.md .project2/skills/README.md .project2/mcp/README.md
git status --short
git commit -m "$(cat <<'EOF'
docs: .project2 경량 하네스 진입점 구조 생성

본문:
- 변경 내용: .project2/에 PROJECT.md 진입점과 agents/·skills/·mcp/ placeholder README 생성
- 변경 이유: 하네스가 프로젝트 코드보다 비대해진 문제를 문서 중심 경량 구조로 해소
- 검증: find로 4개 파일 생성 확인, PROJECT.md 섹션 육안 확인

푸터:
- 후속 작업: 루트 CLAUDE.md를 .project2/PROJECT.md 진입점으로 전환

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

`git status --short` 출력에 `.project2/` 외 파일이 staged(`A `/`M ` 접두)되어 있지 않은지 확인한 뒤 커밋한다.

---

### Task 2: 루트 `CLAUDE.md`를 최소 진입점으로 재작성

Claude Code가 자동 로드하는 루트 `CLAUDE.md`를, 긴 라우팅·역할·규칙 설명을 모두 제거하고 `.project2/PROJECT.md`를 가리키는 최소 포인터로 교체한다. 이 태스크가 진입점을 새 하네스로 전환하는 스위치다. Task 1이 먼저 커밋되어 `.project2/PROJECT.md`가 존재하는 상태에서 수행한다.

**Files:**
- Modify: `CLAUDE.md` (전체 교체)

- [ ] **Step 1: 현재 `CLAUDE.md` 읽기**

Write 도구로 덮어쓰기 전에 Read 도구로 `CLAUDE.md`를 한 번 읽는다 (읽지 않고 덮어쓰면 실패한다). 현재 내용은 SAM 프로젝트 설명 + 작업 진입 흐름 + 에이전트 모델 + 규칙 우선순위 + 문서 정리 원칙 + 경로 표기로 구성된 긴 문서다.

- [ ] **Step 2: `CLAUDE.md` 전체 교체**

Write 도구로 `CLAUDE.md`를 다음 내용으로 완전히 교체한다.

```markdown
# CLAUDE.md

이 저장소는 컴퓨터 비전 프로젝트 **Object3D Prior**다.

## 작업 진입점

모든 작업 전에 `.project2/PROJECT.md`를 먼저 읽는다. 그 파일이 원칙·금지·방향을 정한다.

프로젝트의 목적·범위·파이프라인 상세는 `docs/README.md`가 단일 출처다.

## 참고

`.claude/`는 이전 하네스다. 새 작업에서 읽지 않는다. `.project2/`가 검증된 뒤 `.claude/`를 대체할 예정이다.
```

- [ ] **Step 3: 검증**

Run: `git diff --stat CLAUDE.md`
Expected: `CLAUDE.md` 한 파일이 변경됨 (대폭 삭제 + 소폭 추가).

이어서 `CLAUDE.md`를 읽어 `.project2/PROJECT.md`를 가리키는지, 기존의 `.claude/PROJECT.md`·`command-router.md`·11개 역할 언급이 모두 제거됐는지 확인한다.

- [ ] **Step 4: 커밋**

```bash
git add CLAUDE.md
git status --short
git commit -m "$(cat <<'EOF'
docs: 작업 진입점을 .project2/PROJECT.md로 전환

본문:
- 변경 내용: 루트 CLAUDE.md를 .project2/PROJECT.md를 가리키는 최소 포인터로 재작성
- 변경 이유: 비대한 라우팅·역할·규칙 설명을 진입점에서 제거하고 경량 하네스로 전환
- 검증: git diff로 변경 확인, CLAUDE.md가 새 진입점을 가리키는지 육안 확인

푸터:
- 관련 이슈: 없음
- 후속 작업: .claude/settings.json 훅 정리 (별도 승인 필요)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

`git status --short` 출력에 `CLAUDE.md` 외 파일이 staged되어 있지 않은지 확인한 뒤 커밋한다.

---

### Task 3: `.claude/settings.json` 훅 정리 — 사용자 승인 필요

**이 태스크는 사용자의 명시적 승인 전에 실행하지 않는다.** 기존 하네스 동작을 바꾸는 변경이기 때문이다.

현재 `.claude/settings.json`은 두 hook을 가지고 있다.

- `SessionStart` — `'[프로젝트 진입] 작업 전 .claude/PROJECT.md 와 .claude/agents/routing/command-router.md 를 읽고 ...'` 문구를 주입
- `UserPromptSubmit` — `'[라우팅 확인] 응답 전 ... .claude/agents/routing/command-router.md 기준으로 분류하세요.'` 문구를 매 턴 주입

이 문구들은 제거되는 옛 하네스(`command-router.md`, 11개 역할)를 가리키므로, 새 진입점(`CLAUDE.md` → `.project2/PROJECT.md`)과 충돌하는 노이즈다.

**Files:**
- Modify: `.claude/settings.json`

- [ ] **Step 1: 사용자 승인 요청**

다음 제안을 사용자에게 제시하고 명시적 승인을 받는다.

> 제안: `.claude/settings.json`의 `SessionStart`·`UserPromptSubmit` 두 hook을 모두 제거한다. 새 진입점 안내는 루트 `CLAUDE.md`(자동 로드)가 이미 담당하므로 hook이 중복·노이즈다. `worktree.bgIsolation` 설정은 그대로 유지한다 (project/ 가 gitignore라 worktree 격리가 불가능하므로 필요).

승인을 받지 못하면 이 태스크를 건너뛰고 계획을 종료한다 (`.claude/settings.json`은 변경하지 않는다).

- [ ] **Step 2: (승인 후) `.claude/settings.json` 교체**

Read 도구로 `.claude/settings.json`을 읽은 뒤, Write 도구로 다음 내용으로 교체한다.

```json
{
  "worktree": {
    "bgIsolation": "none"
  }
}
```

- [ ] **Step 3: 검증**

Run: `git diff .claude/settings.json`
Expected: `hooks` 블록 전체가 삭제되고 `worktree` 블록만 남음.

JSON이 유효한지 확인:
Run: `python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "valid json"`
Expected: `valid json`

- [ ] **Step 4: 커밋**

```bash
git add .claude/settings.json
git status --short
git commit -m "$(cat <<'EOF'
chore: 옛 하네스 라우팅 hook 제거

본문:
- 변경 내용: .claude/settings.json의 SessionStart·UserPromptSubmit hook 제거
- 변경 이유: 제거된 옛 하네스(command-router, 역할)를 가리키는 문구가 새 진입점과 충돌
- 검증: git diff로 hooks 블록 삭제 확인, json.load로 유효성 확인

푸터:
- 관련 이슈: 없음
- 후속 작업: .project2/ 검증 후 .claude/ 교체 (Phase 2, 별도 작업)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 범위 밖 (이 계획에서 하지 않음)

다음은 설계 문서의 Phase 2이며 검증 후 별도 작업으로 수행한다.

- `.claude/`를 `.claude-legacy/`로 archive
- `.project2/`를 `.claude/`로 rename
- `CLAUDE.md` 포인터를 `.claude/PROJECT.md`로 갱신

또한 이 계획은 `agents/`·`skills/`·`mcp/`에 실제 콘텐츠를 만들지 않는다. 하네스 성장 규칙에 따라 반복 고통이 확인될 때 항목 하나씩 사용자 승인 후 추가한다.

## 완료 기준

- Task 1, Task 2 커밋 완료. `.project2/`에 4개 파일, `CLAUDE.md`가 `.project2/PROJECT.md`를 가리킴.
- Task 3는 사용자 승인 시 커밋 완료, 미승인 시 건너뜀.
- `.claude/`의 다른 파일(roles, rules, agents 등)은 변경되지 않음.
