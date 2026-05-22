# src

이 폴더는 객체 인식 기반 3D 공간 보조 프로젝트의 실제 구현 코드를 담는다.

초기 목표는 방 전체를 한 번에 복원하는 것이 아니라, 스마트폰 영상 속 단일 객체를 SAM 계열 모델로 추적하고 depth/pose와 결합해 3D object prior를 만드는 것이다.

## 구현된 MVP 모듈

- `object3d.capture`: frame sampling, 촬영 metadata, manifest 생성
- `object3d.contracts`: mask, geometry, point cloud, object prior 데이터 계약
- `object3d.adapters.segmentation.mock`: SAM/SAM2 연동 전 mock mask adapter
- `object3d.adapters.segmentation.sam`: SAM/SAM2 predictor 출력을 `MaskRecord`로 변환하는 adapter contract
- `object3d.adapters.segmentation.manual`: 실제 모델 없이 수동 prompt를 mask로 바꾸는 manual predictor
- `object3d.adapters.geometry.mock`: 실 geometry 모델 연동 전 mock depth/pose adapter
- `object3d.geometry`: masked back-projection
- `object3d.reconstruction`: object point cloud fusion
- `object3d.priors`: bbox 기반 object prior fitting
- `object3d.evaluation`: 실측값 대비 dimension error 계산
- `object3d.visualization`: point cloud PLY export, mask overlay export
- `object3d.pipeline`: mock 기반 end-to-end 실행 흐름

첫 MVP는 실제 SAM/SAM2와 MapAnything/VGGT를 바로 붙이지 않는다.
먼저 contract와 downstream geometry pipeline을 검증한 뒤 실제 adapter를 추가한다.

`object3d.adapters.segmentation.sam`은 실제 모델 dependency를 기본 설치에 강제하지 않는다.
SAM/SAM2 predictor 객체를 외부에서 주입하면 `MaskRecord`로 정규화하고,
실제 predictor 생성은 `load_sam_predictor()`의 optional lazy import 경로로 분리한다.

## Mock MVP 실행

아직 패키지 설치 설정을 두지 않았으므로 로컬 실행은 `PYTHONPATH=src`를 붙인다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp
```

실행하면 다음 산출물이 생성된다.

- `outputs/mock-mvp/summary.json`: 객체 prior, 치수 오차, PLY 경로 요약
- `outputs/mock-mvp/object_001_cloud.ply`: mock 객체 point cloud

## 수동 Prompt Segmentation 실행

실제 SAM/SAM2 설치 전에는 box prompt를 직접 mask로 바꾸는 manual predictor로
입력/출력 포맷을 검증할 수 있다.

prompt JSON 예시:

```json
{
  "box_xyxy": [20, 30, 180, 160]
}
```

실행:

```bash
PYTHONPATH=src python3 -m object3d.pipeline.segment_image \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/manual-segmentation \
  --object-id object_001
```

산출물:

- `outputs/manual-segmentation/mask.npy`
- `outputs/manual-segmentation/overlay.png`
- `outputs/manual-segmentation/summary.json`

## SAM2 Segmentation 실행 경로

SAM2 dependency와 checkpoint/config 파일은 저장소에 포함하지 않는다.
로컬 환경에 SAM2를 설치하고 checkpoint/config 경로를 준비한 뒤 `sam2` backend를 사용한다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline.segment_image \
  --backend sam2 \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/sam2-segmentation \
  --checkpoint-path checkpoints/sam2.1_hiera_tiny.pt \
  --config-path configs/sam2.1/sam2.1_hiera_t.yaml \
  --device cpu \
  --object-id object_001
```

SAM2가 설치되어 있지 않으면 `OptionalSegmentationDependencyError`로 실패한다.
이 실패는 의도된 동작이며, 기본 mock/manual pipeline은 SAM2 설치 없이도 계속 동작해야 한다.
