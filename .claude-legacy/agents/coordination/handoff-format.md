# 공통 인계 형식

이 파일은 모든 라우팅된 agent가 작업을 마칠 때 남기는 공통 인계(handoff) 블록을 정의하는 canonical 형식이다. `command-router.md`, `orchestrator-rules.md`, 각 역할 문서, worker result는 모두 이 형식을 기준으로 삼는다.

## 인계 블록

```text
담당:
입력:
출력:
검증:
위험:
실패 기록:
필요 리뷰:
커밋 제안:
작업 폴더:
다음 담당:
```

## 규칙

- 역할 문서가 역할별 산출물 항목(예: normalized mask contract, coordinate contract)을 추가로 정의하면, 그 항목을 채운 뒤 위 공통 인계 블록으로 마무리한다.
- 멀티에이전트 작업의 worker는 이 블록을 `.claude/tasks/<task-name>/workers/<role>/result.md`에 저장한다.
- 인계는 한 화면 안에 들어오도록 짧게 유지한다. 큰 출력은 task artifact로 저장하고 경로만 남긴다.
- 빈 항목은 "없음"으로 명시한다. 항목을 조용히 생략하지 않는다.
