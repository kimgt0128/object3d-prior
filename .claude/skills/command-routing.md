# Command Routing 스킬

## 목적

사용자 요청에 대해 가장 작은 올바른 owner와 context set을 선택한다.

## 사용할 때

새 사용자 요청이 들어왔고 누가 작업을 소유해야 하는지 결정해야 할 때 사용한다.

## 사용하지 않을 때

- 선택된 owner가 이미 로드되어 있고 요청이 바로 이어지는 작업이다.
- 프로젝트 라우팅 없이 답할 수 있는 좁은 사실 질문이다.

## 절차

1. `.claude/PROJECT.md`를 읽는다.
2. `.claude/agents/routing/command-router.md`를 읽는다.
3. 요청 의도를 파악한다.
4. primary owner를 하나 선택한다.
5. 정말 필요할 때만 supporting agent를 선택한다.
6. primary owner 파일을 읽는다.
7. 관련 skill 파일을 읽는다.
8. 해당 ownership boundary 안에서만 실행, 계획, 리뷰한다.

## 소유권 규칙

최종 artifact는 owner 하나가 책임진다. supporting agent는 입력 또는 리뷰만 제공한다.

## escalation 규칙

다음 경우 Review Orchestrator로 올린다.

- 둘 이상의 pipeline module이 바뀐다.
- coordinate transform이 바뀐다.
- measurement logic이 바뀐다.
- repository structure가 바뀐다.
- final demo behavior가 바뀐다.

## 출력

```text
명령 의도:
주 담당:
선택 skill:
참고 문서:
읽지 않은 context:
다음 작업:
```
