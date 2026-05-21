# Visual Demo 스킬

## 목적

파이프라인 결과를 구체적인 2D/3D 근거로 이해 가능하게 만든다.

## 사용할 때

보고서, 발표, interactive demo output을 준비할 때 사용한다.

## 사용하지 않을 때

- core model output이 아직 없다.
- visualization 전에 geometry math를 고쳐야 한다.
- demo가 confidence나 failure warning을 숨기게 된다.

## 필수 view

1. raw frame + object mask overlay
2. sampled frame이 포함된 camera trajectory
3. object-level point cloud
4. dimension label이 포함된 3D bounding box
5. confidence 또는 warning panel
6. 선택 사항: placement feasibility view

## 권장 도구

- Rerun: 2D/3D timeline 통합 시각화
- Open3D: point cloud debugging
- Gradio: 간단한 upload/result demo

## 절차

1. 현재 milestone을 증명하는 가장 작은 visual story를 고른다.
2. raw input, intermediate evidence, final object prior를 함께 보여준다.
3. confidence 또는 warning state를 포함한다.
4. screenshot 또는 recording을 task artifact에 저장한다.

## 출력

```text
demo artifact:
포함 view:
부족한 근거:
표시한 warning:
보고서용 asset:
```
