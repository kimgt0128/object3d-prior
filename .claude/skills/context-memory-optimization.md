# Context Memory Optimization 스킬

## 목적

stale log, broad docs, repeated summary, 과도한 handoff 때문에 agent context가 낭비되는 것을 막는다.

## 사용할 때

- 요청에 context, memory, token, compaction, orchestration, handoff, agent coordination이 포함된다.
- agent가 같은 파일을 반복해서 읽고 있다.
- handoff가 너무 길어 빠르게 검토하기 어렵다.
- 여러 agent가 chat transcript 공유 없이 상태를 공유해야 한다.

## 사용하지 않을 때

- 단발성 설명 요청이다.
- `PROJECT.md`, `agents/routing/command-router.md`, agent 파일 하나, skill 파일 하나로 충분하다.
- 아직 해결되지 않은 debug error output을 계속 봐야 한다.

## 절차

1. context를 부풀리는 원인을 찾는다.
2. 큰 내용은 `.claude/tasks/<task-name>/artifacts/`에 저장하고 handoff에는 짧은 경로만 남긴다.
3. 읽은 파일, 변경 파일, 결정, 오류, 다음 owner가 포함된 artifact index를 유지한다.
4. 전체 context 전달 대신 scoped instruction을 우선한다.
5. phase boundary 또는 반복 re-read가 보이면 compaction을 수행한다.
6. compact state를 다음 질문으로 검증한다.
   - 활성 Issue는 무엇인가?
   - 변경 파일은 무엇인가?
   - 아직 열린 결정은 무엇인가?
   - 다음 agent가 반복하지 말아야 할 것은 무엇인가?

## 출력

```text
context risk:
저장한 artifact:
artifact index:
compaction 결정:
다음에 읽을 context:
읽지 말 것:
```
