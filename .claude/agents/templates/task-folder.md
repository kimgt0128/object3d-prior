# 작업 폴더 생성 가이드

다음 구조로 만든다.

```text
.claude/tasks/<task-name>/
  task.md
  context.md
  log.md
  sources/
  workers/<role>/brief.md
  workers/<role>/result.md
  artifacts/
```

## 규칙

- 계획된 작업과 worker 조율에는 `.claude/tasks/`를 사용한다.
- 실험/run artifact는 task folder 안의 `artifacts/`에 둔다.
- task folder는 local issue draft 또는 GitHub Issue와 연결한다.
- 큰 raw video, checkpoint, point cloud를 여기에 넣지 않는다.
