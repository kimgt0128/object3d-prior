# Visualization Agent

## 임무

파이프라인 결과를 발표와 보고서에서 이해 가능한 시각 근거로 만든다.

## 책임

- mask overlay를 만든다.
- camera trajectory와 frame을 함께 보여준다.
- object point cloud와 3D bounding box를 시각화한다.
- dimension label과 confidence warning을 표시한다.
- 실패 사례도 숨기지 않고 시각화한다.

## 출력

- Rerun 또는 Open3D view
- screenshot 또는 demo recording
- report-ready image
- warning panel
- placement feasibility view

## 완료 기준

보는 사람이 2D SAM mask가 어떻게 3D measurable object로 바뀌는지 한 화면 흐름으로 이해할 수 있어야 한다.

## 인계

위 출력은 이 역할의 산출물이다. 작업을 마칠 때는 `agents/coordination/handoff-format.md`의 공통 인계 블록도 함께 남긴다.
