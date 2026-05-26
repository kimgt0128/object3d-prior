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
- `object3d.priors`: axis-aligned/PCA oriented bbox 기반 object prior fitting
- `object3d.evaluation`: 실측값 대비 dimension error 계산
- `object3d.visualization`: point cloud PLY, oriented bbox PLY, scene manifest, optional viewer, mask overlay export
- `object3d.pipeline`: mock 기반 end-to-end 실행 흐름

첫 MVP는 실제 SAM/SAM2와 MapAnything/VGGT를 바로 붙이지 않는다.
먼저 contract와 downstream geometry pipeline을 검증한 뒤 실제 adapter를 추가한다.

`object3d.adapters.segmentation.sam`은 실제 모델 dependency를 기본 설치에 강제하지 않는다.
SAM/SAM2 predictor 객체를 외부에서 주입하면 `MaskRecord`로 정규화하고,
실제 predictor 생성은 `load_sam_predictor()`의 optional lazy import 경로로 분리한다.

`object3d.adapters.geometry.file`은 실제 depth/pose 모델을 바로 실행하지 않고,
각 모델이 만든 geometry 산출물을 공통 `.npz` 파일로 받은 뒤 `GeometryRecord`로
정규화한다.

## Mock MVP 실행

아직 패키지 설치 설정을 두지 않았으므로 로컬 실행은 `PYTHONPATH=src`를 붙인다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp
```

실행하면 다음 산출물이 생성된다.

- `outputs/mock-mvp/summary.json`: 객체 prior, 치수 오차, PLY 경로 요약
- `outputs/mock-mvp/object_001_cloud.ply`: mock 객체 point cloud
- `outputs/mock-mvp/object_001_bbox.ply`: oriented bbox edge PLY
- `outputs/mock-mvp/scene_manifest.json`: viewer 연동용 scene manifest

`summary.json`에는 `bbox_type`, `center_xyz`, `axes`, `dimensions_m`,
`dimension_errors`, `point_cloud_ply`, `bbox_ply`, `scene_manifest_json`이 포함된다.
현재 mock MVP는 PCA 기반 `oriented` bbox를 기본으로 사용한다.

## Scene Viewer 실행

`scene_manifest.json`을 생성한 뒤 dependency 없이 summary를 확인할 수 있다.

```bash
PYTHONPATH=src python3 -m object3d.visualization.view_scene \
  --manifest outputs/mock-mvp/scene_manifest.json \
  --backend summary
```

Rerun을 설치한 환경에서는 같은 manifest를 Rerun viewer backend로 보낼 수 있다.
Rerun은 선택 dependency이며 기본 테스트/실행에는 필요하지 않다.

```bash
uv pip install --python .venv/bin/python rerun-sdk
PYTHONPATH=src python3 -m object3d.visualization.view_scene \
  --manifest outputs/mock-mvp/scene_manifest.json \
  --backend rerun \
  --spawn
```

GUI를 바로 띄우지 않고 재현 가능한 recording 파일로 저장할 수도 있다.

```bash
PYTHONPATH=src .venv/bin/python -m object3d.visualization.view_scene \
  --manifest outputs/mock-mvp/scene_manifest.json \
  --backend rerun \
  --save-rrd outputs/mock-mvp/object3d-prior.rrd
```

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

## Segmentation 결과를 3D Prior로 변환

`segment_image`가 만든 `summary.json`을 다음 단계 입력으로 넘기면,
잘라낸 객체 mask를 mock depth 평면에 올려 3D point cloud와 bbox를 만들 수 있다.
쉽게 말하면 "2D로 자른 객체"를 "3D 크기 추정" 단계로 넘기는 명령이다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/manual-segmentation/summary.json \
  --output-dir outputs/prior-from-mask \
  --depth-m 2.0
```

현재 `--depth-m`은 실제 depth 모델이 붙기 전 임시 깊이 값이다.
그래도 mask, back-projection, bbox, scene artifact 흐름을 한 번에 검증할 수 있다.

산출물:

- `outputs/prior-from-mask/summary.json`
- `outputs/prior-from-mask/object_001_cloud.ply`
- `outputs/prior-from-mask/object_001_bbox.ply`
- `outputs/prior-from-mask/scene_manifest.json`

실제 depth/pose 모델을 붙이기 전에는 공통 `.npz` 파일을 만들어 같은 CLI에
넘길 수 있다.

필수 key:

- `depth_m`: meter 단위 `(H, W)` depth map
- `intrinsics`: `(3, 3)` pinhole camera matrix
- `camera_to_world`: camera 좌표계를 world 좌표계로 보내는 `(4, 4)` transform

`world_to_camera`는 내부 계약에서 받지 않는다. 필요한 경우 외부 모델 산출물을
`camera_to_world`로 변환한 뒤 저장한다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/manual-segmentation/summary.json \
  --output-dir outputs/prior-from-mask-file-geometry \
  --geometry-npz outputs/geometry/frame_000000.npz
```

이 경로는 아직 MapAnything/VGGT/COLMAP inference를 실행하지 않는다. 목적은
모델별 adapter가 만든 depth/pose 파일이 downstream 3D prior 파이프라인에
같은 계약으로 들어갈 수 있는지 확인하는 것이다.

## 대표 Smoke Fixture 생성

실제 사용자 사진은 저장소에 커밋하지 않는다. 대신 실제 사진 검증에서
안정적이었던 대표 케이스를 synthetic 이미지와 prompt로 재현해 smoke
test에 사용한다.

현재 대표 성공 케이스는 다음 3개다.

- 노트북
- 영수증
- 태블릿+키보드

fixture 생성:

```bash
PYTHONPATH=src python3 -m object3d.pipeline.generate_smoke_fixtures \
  --output-dir outputs/representative-smoke-fixtures
```

생성되는 파일:

- `outputs/representative-smoke-fixtures/manifest.json`
- `outputs/representative-smoke-fixtures/<case_id>/image.png`
- `outputs/representative-smoke-fixtures/<case_id>/prompt.json`
- `outputs/representative-smoke-fixtures/<case_id>/metadata.json`

이 fixture는 실제 치수 검증용이 아니다. 원본 개인 사진 없이도
`segment_image -> prior_from_mask` 흐름을 반복 검증하기 위한
작은 재현 입력이다.

## SAM2 결과를 3D Prior까지 연결

SAM2로 만든 `summary.json`도 같은 방식으로 3D prior 단계에 넣을 수 있다.
즉, "SAM2가 자른 객체"를 바로 "3D 점구름과 bbox"로 바꿔볼 수 있다.

```bash
PYTHONPATH=src .venv/bin/python -m object3d.pipeline.segment_image \
  --backend sam2 \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/sam2-to-prior/segmentation \
  --checkpoint-path checkpoints/sam2.1_hiera_tiny.pt \
  --config-path configs/sam2.1/sam2.1_hiera_t.yaml \
  --device cpu \
  --object-id object_001

PYTHONPATH=src .venv/bin/python -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/sam2-to-prior/segmentation/summary.json \
  --output-dir outputs/sam2-to-prior/prior \
  --depth-m 2.0

PYTHONPATH=src .venv/bin/python -m object3d.visualization.view_scene \
  --manifest outputs/sam2-to-prior/prior/scene_manifest.json \
  --backend rerun \
  --save-rrd outputs/sam2-to-prior/prior/sam2-to-prior.rrd
```

마지막 명령은 나중에 다시 열어볼 수 있는 Rerun 3D 장면 파일을 만든다.
이 파일도 `outputs/` 아래에 생기므로 git에는 커밋하지 않는다.

## SAM2 Segmentation 실행 경로

SAM2 dependency와 checkpoint/config 파일은 저장소에 포함하지 않는다.
로컬 환경에 SAM2를 설치하고 checkpoint/config 경로를 준비한 뒤 `sam2` backend를 사용한다.

예시 설치:

```bash
uv venv .venv --python /opt/homebrew/bin/python3.11
uv pip install --python .venv/bin/python torch torchvision opencv-python \
  'git+https://github.com/facebookresearch/sam2.git'
```

예시 checkpoint 준비:

```bash
mkdir -p checkpoints
curl -L \
  -o checkpoints/sam2.1_hiera_tiny.pt \
  https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt
```

```bash
PYTHONPATH=src .venv/bin/python -m object3d.pipeline.segment_image \
  --backend sam2 \
  --image-path examples/frame.png \
  --prompt-json examples/prompt.json \
  --output-dir outputs/sam2-segmentation \
  --checkpoint-path checkpoints/sam2.1_hiera_tiny.pt \
  --config-path configs/sam2.1/sam2.1_hiera_t.yaml \
  --device cpu \
  --object-id object_001
```

`--config-path`는 SAM2 package 기준 상대 경로를 권장한다.
설치된 package 내부 config 절대 경로를 넘긴 경우에도 adapter가 package 상대 경로로 정규화한다.

SAM2가 설치되어 있지 않으면 `OptionalSegmentationDependencyError`로 실패한다.
이 실패는 의도된 동작이며, 기본 mock/manual pipeline은 SAM2 설치 없이도 계속 동작해야 한다.
