# 작업 폴더

이 폴더는 작업별 오케스트레이션 상태를 저장한다.

사용자 승인을 받은 작업 하나당 하나의 폴더를 만든다.

```text
.claude/tasks/<task-name>/
```

각 작업 폴더는 다음을 포함한다.

- `task.md`: 목표, 상태, owner, worker, write scope
- `context.md`: 짧은 컨텍스트 스냅샷
- `log.md`: append-only 실행 기록
- `workers/<role>/brief.md`: worker별 지시문
- `workers/<role>/result.md`: worker 결과와 검증
- `artifacts/`: 작은 작업 산출물

raw dataset, model checkpoint, 큰 generated output은 여기에 넣지 않는다.
