# Geometry Validation 스킬

## 목적

full fusion이나 measurement를 건드리기 전에 가장 싼 순서로 geometry 문제를 진단한다.

## 사용할 때

depth, pose, point cloud, bounding box 결과가 이상할 때 사용한다.

## 사용하지 않을 때

- mask overlay가 이미 틀렸다.
- git, docs, folder structure 문제다.
- depth, pose, point cloud artifact가 아직 없다.

## 검증 순서

1. camera intrinsics를 확인한다.
2. depth scale을 확인한다.
3. pose convention을 확인한다.
4. 알려진 pixel 하나를 수동으로 back-project한다.
5. frame 하나의 point cloud를 먼저 시각화한다.
6. 인접한 두 frame만 fusion한다.
7. mask 적용 전후 object point cloud를 비교한다.
8. statistical outlier를 제거한다.
9. bounding box를 fitting하고 수동 측정값과 비교한다.

## 흔한 증상

- 객체가 너무 크거나 작다: scale mismatch
- 객체가 중복되어 보인다: pose inconsistency
- 평면이 휘어 보인다: intrinsics 또는 lens distortion 문제
- 객체가 떠 있다: floor plane 또는 pose 오류
- 객체에 배경이 섞인다: mask leakage

## 절차

위 순서대로 확인하고, 실패를 설명하는 첫 계층에서 멈춘다. one-frame geometry가 믿을 만해지기 전에는 fusion, bbox, placement logic을 튜닝하지 않는다.

## 출력

```text
증상:
확인한 계층:
원인 추정:
근거:
변경한 파라미터:
before/after artifact:
다음 확인:
```
