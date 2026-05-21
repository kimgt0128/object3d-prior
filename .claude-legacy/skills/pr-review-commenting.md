# PR Review Commenting 스킬

## 목적

리뷰 finding이 local chat이나 log에 갇히지 않고 PR에서 보이게 한다.

## 사용할 때

- PR이 있고 리뷰가 끝났다.
- 사용자가 code review, gstack review, PR review를 요청했다.
- 자동 reviewer가 actionable finding을 냈다.

## 사용하지 않을 때

- PR 또는 remote repository context가 없다.
- 리뷰 output에 민감한 내부 reasoning이 들어 있다.
- finding이 actionable하지 않아 comment noise만 만든다.

## 절차

1. PR 번호 또는 URL을 확인한다.
2. 선택된 review stack을 실행한다.
3. finding을 간결한 한글 PR-safe Markdown으로 바꾼다.
4. 기본적으로 general PR review comment를 남긴다.
5. 정확한 diff line이 있는 finding만 inline comment로 남긴다.
6. 관련 failure note가 있으면 연결한다.

## 권장 명령

```text
gh pr review <number-or-url> --comment --body-file <review.md>
```

## 댓글 규칙

- vague comment를 남기지 않는다.
- duplicate finding을 남기지 않는다.
- 내부 reasoning trace를 노출하지 않는다.
- 정책이 없으면 approve/request-changes를 자동으로 선택하지 않는다.
- required fix, optional note, verification gap, merge risk를 포함한다.
- PR review comment는 한글로 작성한다.

## 한글 리뷰 comment 템플릿

```markdown
## 자동 리뷰 요약

### 적용한 리뷰 계층
- 스펙 준수:
- 검증 근거:
- 도메인 리뷰:
- 통합 영향:

### 수정 필요

### 권장 개선

### 선택 사항

### 병합 전 확인

### 오케스트레이터 참고 사항
```

## 출력

```text
PR:
review body 경로:
comment 명령:
게시 여부:
병합 영향 finding:
다음 담당:
```
