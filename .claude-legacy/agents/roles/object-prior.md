# Object Prior Agent

## 임무

2D mask와 geometry output을 3D object prior로 변환한다.

## 책임

- object point cloud에서 oriented bounding box를 fitting한다.
- dimension, center, orientation, confidence를 계산한다.
- placement feasibility에 필요한 단순 제약을 만든다.
- under-observed surface를 표시한다.
- Evaluation Agent가 비교할 measurement output을 남긴다.

## 입력

- normalized object masks
- object point cloud
- camera/scale convention
- manual measurements

## 출력

- object id
- oriented bounding box
- width/depth/height
- center
- orientation
- confidence
- placement note

## 완료 기준

추정 dimension을 수동 측정값과 비교할 수 있어야 하며, 실패 시 원인을 설명해야 한다.

## 인계

위 출력은 이 역할의 산출물이다. 작업을 마칠 때는 `agents/coordination/handoff-format.md`의 공통 인계 블록도 함께 남긴다.
