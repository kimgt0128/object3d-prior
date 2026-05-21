# 리뷰와 검증 규칙

이 파일은 코드, 문서, 파이프라인 변경이 완료됐다고 주장하기 전 필요한 검증 기준을 정하는 canonical 규칙이다.

## 리뷰 계층 순서

리뷰는 단일 pass가 아니다. 낮은 계층에서 실패하면 상위 리뷰로 넘어가지 않는다.

1. Self-check — 구현자가 범위와 검증을 스스로 확인
2. Spec compliance — Issue/task 요구사항과 일치 확인
3. Evidence — test, metric, screenshot, visual check 확인
4. Domain lens — CV domain 오류 확인 (segmentation/geometry/measurement)
5. Integration — 다음 agent와 output contract 확인

계층별 상세 흐름과 멈출 조건 표는 `rules/ref/review-stack.md`, domain별 checklist는 `rules/ref/review-lenses.md`를 연다.

## 공통 규칙

- spec과 다르면 style review로 넘어가지 않는다.
- test 또는 visual evidence가 없으면 “좋아 보임”으로 승인하지 않는다.
- geometry나 measurement 변경은 domain review 없이 넘기지 않는다.
- PR이 있으면 review finding을 PR comment로 남긴다.
- 내부 reasoning trace를 PR comment에 노출하지 않는다.

## Domain별 필수 검증

Segmentation:

- frame 위 mask overlay 확인
- object id consistency 확인
- confidence 또는 mask area anomaly 기록
- raw mask와 filtered mask 분리

Geometry:

- camera intrinsics 기록
- depth scale convention 기록
- pose convention 기록
- fusion 전 1프레임 point cloud 확인
- multi-frame 전 2프레임 fusion 확인

Reconstruction:

- object mask 적용 후 object cloud export
- outlier filtering parameter 기록
- object cloud와 background 분리 확인

Object prior:

- axis convention 기록
- axis-aligned box와 oriented box 구분
- 치수를 단위와 함께 보고
- confidence가 데이터 품질을 반영
- 정확도 주장 전 수동 실측값 비교

Evaluation:

- manual ground truth 기록
- absolute error와 relative error 보고
- 실패 사례 포함
- ablation이 실제 pipeline 선택과 연결

Visualization:

- raw frame과 mask overlay 표시
- camera trajectory와 object cloud 표시
- 3D bounding box와 dimension label 표시
- warning 또는 confidence 표시

## 완료 주장 전 멈출 조건

- 검증 명령 또는 시각 artifact가 없다.
- 실패 frame이 제외된 이유가 없다.
- metric이 명백한 실패를 숨긴다.
- output contract가 downstream과 맞는지 확인하지 않았다.
