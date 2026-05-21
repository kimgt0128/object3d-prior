# Object Prior Fitting 스킬

## 목적

추적된 mask와 geometry output을 측정 가능한 3D object prior로 변환한다.

## 사용할 때

- bbox, dimension, orientation, placement, fit check, object prior를 다룬다.
- segmentation mask와 depth 또는 point cloud output을 객체 단위 contract로 합쳐야 한다.
- 물리적 측정값을 기준으로 평가해야 한다.

## 사용하지 않을 때

- mask identity consistency를 아직 확인하지 않았다.
- depth, pose, point cloud artifact가 없다.
- SAM만 실행하거나 geometry model만 실행하는 작업이다.

## 절차

1. frame 간 mask identity consistency를 확인한다.
2. normalized geometry output으로 mask pixel만 back-project한다.
3. object point를 outlier filtering과 함께 fusion한다.
4. oriented bounding box를 fitting하고 axis convention을 기록한다.
5. dimension, center, orientation, confidence를 계산한다.
6. 가능하면 수동 측정값과 비교한다.
7. 덜 관측된 표면과 placement risk를 표시한다.

## 출력

```text
객체 id:
입력 mask:
geometry source:
point cloud artifact:
bounding box:
dimension:
orientation:
confidence:
placement note:
failure risk:
```
