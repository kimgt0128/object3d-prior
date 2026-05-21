# Model Adapter 스킬

## 목적

외부 모델 repository의 불안정한 output format이 프로젝트 핵심 로직으로 새지 않게 막는다.

## 사용할 때

SAM, MapAnything, VGGT, COLMAP 또는 다른 pretrained model을 추가하거나 교체할 때 사용한다.

## 사용하지 않을 때

- bounding box, measurement, placement logic을 작성하는 중이다.
- 이미 normalized output이 있는데 geometry convention만 디버깅한다.
- 구현 없이 개념 조사만 한다.

## 규칙

외부 모델 코드는 프로젝트 소유의 안정적인 interface 뒤에 감춘다. 모델별 raw output format을 전체 프로젝트로 퍼뜨리지 않는다.

## 필수 adapter output

Segmentation adapter:

- frame id
- object id
- binary mask
- confidence
- prompt type

Geometry adapter:

- frame id
- depth map
- camera intrinsics
- camera pose
- coordinate convention
- confidence 또는 quality score

## 절차

1. 외부 모델의 raw output format을 확인한다.
2. 프로젝트 소유 normalized contract를 정의한다.
3. raw output과 normalized output을 분리해 저장한다.
4. downstream geometry가 사용하기 전에 visual sanity check를 추가한다.

## 출력

```text
모델:
버전:
raw output 경로:
normalized contract:
알려진 한계:
sanity check:
다음 담당:
```
