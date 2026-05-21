# Segmentation Agent

## 임무

SAM 계열 모델을 사용해 객체 mask와 tracking identity를 안정적으로 생성한다.

## 책임

- SAM/SAM2/GroundingDINO류 모델 adapter contract를 정의한다.
- frame별 binary mask와 object id를 유지한다.
- mask confidence, area 변화, drift를 기록한다.
- Object Prior Agent가 사용할 normalized mask output을 만든다.
- mask 품질이 geometry 실패로 전파되지 않게 한다.

## 입력

- sampled frames
- prompt 또는 text query
- capture metadata

## 출력

- frame id
- object id
- binary mask
- confidence
- prompt type
- mask quality warning

## 완료 기준

같은 객체가 여러 frame에서 같은 id로 유지되고, overlay로 mask 품질을 확인할 수 있어야 한다.

## 인계

위 출력은 이 역할의 산출물이다. 작업을 마칠 때는 `agents/coordination/handoff-format.md`의 공통 인계 블록도 함께 남긴다.
