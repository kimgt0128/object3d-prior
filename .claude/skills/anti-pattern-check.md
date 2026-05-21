# Anti-Pattern Check 스킬

## 목적

구현 또는 리뷰 전에 이미 알고 있는 나쁜 방향으로 흐르는 것을 막는다.

## 사용할 때

- 사용자가 risk, forbidden path, “하지 말아야 할 것”을 묻는다.
- full-room reconstruction, full model training, broad rewrite가 계획에 들어온다.
- architecture, routing, data storage, git, external model output을 건드린다.

## 사용하지 않을 때

- 프로젝트 액션이 없는 좁은 설명 요청이다.
- 특정 domain skill이 이미 해당 stop condition을 포함한다.
- 사용자가 명시적으로 project constraint를 무시하라고 했다.

## 절차

1. `rules/business-logic.md`를 읽는다.
2. 제안 작업이 context, data, model, geometry, review, git constraint를 위반하는지 확인한다.
3. 위반한다면 가장 작은 안전한 대안을 제시한다.
4. 의도적인 trade-off라면 진행 전 decision brief를 요구한다.

## 출력

```text
확인 영역:
발동된 anti-pattern:
더 안전한 대안:
결정 필요:
다음 담당:
```
