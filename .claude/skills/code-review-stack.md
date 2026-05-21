# Code Review Stack 스킬

## 목적

위험한 구현 변경이 얕은 단일 리뷰만 통과하지 않도록 계층형 리뷰를 적용한다.

## 사용할 때

agent 작업을 다음 구현 slice로 넘기기 전에 리뷰할 때 사용한다.

## 사용하지 않을 때

- 동작 영향이 없는 아주 작은 typo 수정이다.
- 계획만 요청받았다.
- 리뷰할 diff 또는 artifact가 없다.

## 리뷰 순서

1. 구현자 self-check
2. spec compliance review
3. test 또는 visual verification
4. domain-specific review
5. 중요한 diff에는 Compound Engineering style review
6. 최종 demo 또는 PR 전 integration review

## 작은 변경의 최소 리뷰

작은 문서 또는 config 변경:

- self-check
- spec compliance
- commit rule check

작은 코드 변경:

- self-check
- focused test
- geometry, segmentation, measurement를 건드리면 domain review

## CV pipeline 변경 필수 리뷰

Segmentation:

- frame 위 mask overlay 확인
- object id consistency 확인
- confidence 또는 mask area anomaly 기록

Geometry:

- one-frame point cloud 시각화
- depth scale과 pose convention 확인
- coordinate transform 문서화

Object prior:

- dimension을 수동 측정값과 비교
- oriented bounding box axis 확인
- confidence와 failure case 기록

## 절차

1. 변경 파일과 영향을 받는 pipeline stage를 확인한다.
2. `agents/routing/command-router.md`의 최소 리뷰 깊이를 적용한다.
3. 필요한 domain만 `rules/ref/review-lenses.md`에서 읽는다.
4. finding을 blocking, should-fix, optional로 나눈다.
5. PR이 있으면 `pr-review-commenting.md`로 PR-visible finding을 남긴다.

## 출력

```text
리뷰 계층:
검토 파일:
finding:
필수 수정:
검증 공백:
PR comment 필요 여부:
```
