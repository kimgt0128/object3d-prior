# 컨텍스트, 메모리, 오케스트레이션 정책

이 파일은 context 최적화, handoff, memory 관리, multi-agent coordination을 다룰 때만 연다.

## 참고 원칙

- context는 저장소가 아니라 제한된 attention budget으로 본다.
- 먼저 이름과 짧은 설명만 읽고, 전체 내용은 트리거가 있을 때만 연다.
- 계획, handoff, log, 큰 출력은 파일 시스템을 durable memory로 사용한다.
- 요청당 token이 아니라 작업당 token 효율을 최적화한다.
- multi-agent는 주로 context isolation이 필요할 때 쓴다. 역할을 과하게 늘리지 않는다.

## 컨텍스트 예산 규칙

- `rg`, 파일명, index로 좁힐 수 있으면 폴더 전체를 읽지 않는다.
- 긴 terminal, web, model output을 handoff에 그대로 붙이지 않는다.
- 해결되지 않은 debugging error는 압축하거나 생략하지 않는다.
- 요약이 artifact tracking을 대체하게 하지 않는다.
- 좁은 brief로 충분한데 full context를 넘겨 delegate하지 않는다.

권장 트리거:

| 신호 | 조치 |
|---|---|
| tool output이 대략 2,000단어를 넘음 | 파일로 저장하고 요약과 경로만 반환 |
| 같은 파일을 반복해서 다시 읽음 | artifact index를 만들거나 수리 |
| 긴 작업 단계가 끝남 | 구조화된 요약으로 압축 |
| 독립 하위 작업이 3개 이상 | isolated agent/worktree 고려 |
| 독립 하위 작업이 3개 미만 | coordination 비용을 줄이기 위해 단일 agent 선호 |

## 파일 시스템 메모리 구조

작업 조율과 작은 실험 산출물은 `.claude/tasks/<task-name>/` 아래에 둔다.

```text
.claude/tasks/<task-name>/
  task.md
  context.md
  log.md
  workers/<role>/brief.md
  workers/<role>/result.md
  artifacts/
```

실행 출력, screenshot, 작은 log, export summary는 `.claude/tasks/<task-name>/artifacts/`에 둔다.

사용자가 명시적으로 요청하지 않는 한 raw video, 큰 model output, cache, 생성된 point cloud는 commit하지 않는다.

## Artifact Index 형식

```markdown
# 산출물 인덱스

## 이슈

## 읽은 파일

## 변경한 파일

## 결정 사항

## 실행한 명령

## 관찰한 오류

## 저장한 출력

## 다음 담당자

## 반복 금지
```

긴 산문 요약보다 이 인덱스가 더 중요하다.

## Handoff 봉투

모든 agent handoff는 `agents/coordination/handoff-format.md`의 공통 인계 블록을 사용한다. 한 화면 안에 들어오게 짧게 유지하고 관련 worker result에 저장한다. 더 자세한 내용이 필요하면 현재 task folder의 `artifacts/` 아래 파일로 링크한다.

## 오케스트레이션 제한

- 한 supervisor 아래에서 active agent를 3-5개보다 많이 돌리지 않는다. 필요하면 조율 단위를 나눈다.
- correctness conflict를 다수결로 해결하지 않는다. evidence-backed review, adversarial critique, 사용자 결정을 우선한다.
- 검증되지 않은 agent output을 downstream 사실로 넘기지 않는다.
- 한 agent의 hallucination이 shared state가 되지 않도록 파일 경로나 evidence를 요구한다.
- handoff가 실제 작업보다 커질 정도로 작업을 잘게 쪼개지 않는다.

## 충돌 처리

agent 간 의견이 충돌하면 orchestrator는 먼저 충돌 종류를 분류한다.

- product decision
- architecture decision
- model-stack decision
- evaluation metric decision
- git/merge conflict

프로젝트 규칙만으로 해결할 수 없으면 [decision-brief.md](../../skills/decision-brief.md)를 사용하고 사용자 결정을 기다린다.
