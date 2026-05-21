# PR Merge Orchestration 스킬

## 목적

여러 agent PR을 병합할 때 conflict를 숨기지 않고 안전한 순서를 제안한다.

## 사용할 때

- 여러 PR이 열려 있다.
- 한 PR이 다른 PR에 의존한다.
- 두 agent branch가 관련 파일이나 contract를 건드린다.
- review finding 때문에 병합 결정이 필요하다.

## 사용하지 않을 때

- 의존성이나 conflict가 없는 trivial PR 하나뿐이다.
- 사용자가 local review만 요청했다.
- 필수 check 또는 review가 아직 끝나지 않았다.

## 절차

1. PR과 linked Issue를 나열한다.
2. 각 PR을 independent, stacked, blocked, conflicting으로 분류한다.
3. touched file과 output contract를 확인한다.
4. review finding과 required verification을 확인한다.
5. 병합 순서를 한글로 제안한다.
6. product, architecture, model-stack, destructive git conflict면 한글 decision brief를 만든다.

## 출력

```text
검토한 PR:
병합 분류:
권장 순서:
차단된 PR:
충돌:
사용자 결정 필요 여부:
다음 작업:
```

## 한글 병합 보고 템플릿

```markdown
## 병합 전략 요약

## 검토한 PR

## 병합 순서 제안

## 차단된 PR

## 충돌 및 위험

## 사용자 결정 필요 여부

## 다음 작업
```
