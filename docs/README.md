# Object3D Prior 프로젝트 설명서

이 문서는 컴퓨터 비전 프로젝트 **Object3D Prior**를 처음 접하는 사람이나 Claude/Codex 같은 코딩 에이전트가 프로젝트의 목적, 범위, 기술 방향, 현재 우선순위를 빠르게 이해하기 위한 진입 문서다.

앞으로 기본 작업은 이 `docs/` 폴더를 중심으로 이해한다. 기존 `.claude/` 폴더는 고급 하네스와 과거 실험 구조로 남아 있지만, 기본 작업에서는 먼저 읽지 않는다. 사용자가 명시적으로 요청하거나 병렬 작업, PR 충돌, 복잡한 리뷰, 실패 기록 자동화가 필요할 때만 참고한다.

## 한 줄 요약

**Object3D Prior는 SAM 계열 모델이 만든 2D 객체 mask를 depth, camera pose, point cloud와 결합해 3D 공간에서 객체를 추적·측정·방향 추정·배치 판단할 수 있는 object prior로 확장하는 컴퓨터 비전 프로젝트다.**

## 왜 이 프로젝트를 하는가

일반적인 segmentation 데모는 이미지 안에서 객체 영역을 분리하는 데서 끝난다.

예를 들어 SAM이나 SAM2를 사용하면 이미지나 영상 속에서 특정 객체의 mask를 매우 잘 얻을 수 있다. 하지만 단순 mask만으로는 다음 질문에 답하기 어렵다.

- 이 객체의 실제 크기는 얼마인가?
- 객체는 3D 공간에서 어디에 있는가?
- 객체는 어느 방향으로 놓여 있는가?
- 객체가 바닥에 붙어 있는가, 떠 있는가?
- 이 공간에 다른 물체를 배치할 수 있는가?
- 카메라가 보지 못한 면은 어디인가?

이 프로젝트는 SAM 계열 모델을 단순한 2D segmentation 도구로만 쓰지 않는다.

대신 SAM의 mask와 video tracking 결과를 3D geometry와 결합해, 객체 단위의 3D prior를 만드는 것을 목표로 한다.

여기서 prior란 후속 단계가 사용할 수 있는 구조화된 객체 정보다.

예를 들면 다음과 같다.

```text
ObjectPrior
  - object_id
  - object_name
  - 2D mask history
  - 3D point cloud
  - center position
  - oriented bounding box
  - width / depth / height
  - orientation
  - confidence
  - observed / unobserved surface hint
  - placement constraint
```

즉 이 프로젝트의 핵심은 **"mask를 3D 객체 정보로 승격한다"**는 데 있다.

## 만들고 싶은 서비스의 모습

최종적으로는 사용자가 스마트폰으로 주변 객체를 촬영하면, 시스템이 객체를 인식하고 3D 공간에서 의미 있는 정보를 제공하는 도구를 만들고 싶다.

초기 서비스 시나리오는 다음과 같다.

1. 사용자가 스마트폰으로 책상, 박스, 의자, 모니터 같은 물체를 짧게 촬영한다.
2. 시스템이 영상에서 프레임을 샘플링한다.
3. SAM/SAM2 계열 모델이 목표 객체를 frame마다 분리하고 추적한다.
4. geometry 모델 또는 mock adapter가 각 frame의 depth와 camera pose를 제공한다.
5. mask가 씌워진 픽셀만 3D 공간으로 역투영한다.
6. 여러 frame에서 얻은 객체 point를 하나로 fusion한다.
7. 객체의 oriented bounding box와 실제 크기를 추정한다.
8. 수동 실측값과 비교해 오차와 confidence를 표시한다.
9. Open3D 또는 Rerun으로 mask, point cloud, camera trajectory, bounding box를 시각화한다.

사용자가 기대하는 결과는 단순히 "객체가 보인다"가 아니다.

아래 질문에 답할 수 있어야 한다.

- 이 물체의 대략적인 width, depth, height는 얼마인가?
- 이 물체는 촬영 공간의 어느 위치에 있는가?
- 이 물체는 어느 방향으로 놓여 있는가?
- 측정값을 얼마나 믿을 수 있는가?
- 어떤 입력 frame이나 mask가 결과를 망쳤는가?
- 이 물체와 비슷한 크기의 다른 물체를 같은 공간에 배치할 수 있는가?

## 실용적인 사용 예시

이 프로젝트는 단순 연구 데모가 아니라, 다음과 같은 실용 기능으로 확장될 수 있다.

### 1. 중고거래용 자동 실측 도우미

판매자가 중고 가구나 물체를 스마트폰으로 촬영하면, 시스템이 대략적인 가로·세로·높이를 자동으로 추정한다.

줄자로 직접 재지 않아도 구매자가 크기를 가늠할 수 있다.

### 2. 가구 배치 가능성 판단

방 안의 특정 공간을 촬영하고 객체의 3D 크기와 방향을 추정하면, 다른 물체를 놓을 수 있는지 판단할 수 있다.

초기에는 정교한 인테리어 시뮬레이터가 아니라, 단순한 box-like placement check부터 시작한다.

### 3. 컴퓨터 비전 학습용 통합 데모

수업에서 배운 image processing, camera geometry, homography, feature matching, segmentation, 3D reconstruction 개념을 하나의 실제 파이프라인으로 연결한다.

즉 이 프로젝트는 단순 모델 호출이 아니라, 수업 지식과 최신 foundation model을 연결하는 실습형 프로젝트다.

## 지금 당장 만들 MVP

초기 MVP는 방 전체를 복원하지 않는다.

처음부터 방 전체 3D reconstruction, dense mapping, Seen2Scene 전체 재현, 대규모 3D completion을 시도하면 범위가 너무 커지고 실패 가능성이 높아진다.

따라서 첫 MVP는 다음으로 제한한다.

```text
스마트폰 영상 속 단일 객체 하나를 대상으로,
프레임 샘플링 → mask/tracking → depth/pose contract → masked back-projection
→ object point cloud → oriented bbox → 측정 평가 → 시각화
까지 이어지는 No-Training MVP를 만든다.
```

첫 MVP의 성공 기준은 다음과 같다.

- 입력 영상에서 일정 간격으로 frame을 추출할 수 있다.
- 각 frame에 대해 목표 객체 mask를 얻을 수 있다.
- depth/pose는 처음에는 mock 또는 generic interface로 시작한다.
- mask가 씌워진 픽셀만 3D point로 변환할 수 있다.
- 최소 2개 frame의 object point를 fusion할 수 있다.
- object point cloud에서 oriented bounding box를 계산할 수 있다.
- width, depth, height를 수동 실측값과 비교할 수 있다.
- 결과를 Open3D 또는 Rerun으로 확인할 수 있다.
- 실패한 경우 mask 문제인지, depth 문제인지, pose 문제인지, point cloud 문제인지 분리해서 설명할 수 있다.

## 현재 선택한 개발 전략

현재 전략은 **No-Training First**다.

처음부터 모델을 학습하거나 fine-tuning하지 않는다.

우선 pretrained 모델과 기하학 파이프라인을 조합해 end-to-end 데모를 만든다.

그 다음 반복적으로 실패하는 병목이 확인되면 그때 필요한 부분만 조정한다.

초기 조정 대상은 다음 정도로 제한한다.

- frame sampling rate
- mask confidence threshold
- mask filtering
- depth/pose adapter contract
- point cloud outlier removal
- bbox fitting 방식
- scale alignment

아래 작업은 첫 MVP에서 하지 않는다.

- 방 전체 dense reconstruction
- Seen2Scene 전체 재현
- 3D generative completion 모델 학습
- 대규모 dataset 다운로드
- GPU fine-tuning
- 복잡한 multi-agent orchestration

## 핵심 파이프라인

```text
Input Video
  ↓
Frame Sampling
  ↓
Frame Manifest
  ↓
Segmentation Adapter
  ↓
Mask Records
  ↓
Geometry Adapter
  ↓
Depth / Intrinsics / Pose Records
  ↓
Masked Back-Projection
  ↓
Per-frame Object Point Cloud
  ↓
Point Cloud Fusion
  ↓
Fused Object Cloud
  ↓
Object Prior Fitting
  ↓
Oriented Bounding Box / Dimensions / Orientation / Confidence
  ↓
Evaluation + Visualization
```

## 각 단계의 역할

### T1. Capture

입력 영상이나 이미지 폴더에서 frame을 샘플링한다.

출력은 frame manifest다.

manifest에는 frame id, image path, timestamp, camera metadata, 촬영 대상 실측값이 들어간다.

이 단계는 downstream이 재현 가능한 입력을 받을 수 있게 만드는 것이 목적이다.

### T2. Segmentation

SAM/SAM2 계열 모델을 사용해 목표 객체의 mask를 만든다.

초기에는 실제 모델이 없어도 adapter contract를 먼저 정한다.

중요한 것은 raw model output을 downstream에 그대로 흘리지 않는 것이다.

표준화된 `MaskRecord` 형태로 바꿔야 한다.

### T3. Geometry

MapAnything, VGGT, COLMAP 같은 모델이나 도구가 제공하는 depth, camera intrinsics, pose를 표준화한다.

첫 구현에서는 실모델 연동보다 generic interface와 mock을 먼저 만든다.

이유는 downstream 로직을 실모델 의존성 없이 검증하기 위해서다.

### T4. Masked Back-Projection

2D pixel coordinate와 depth를 사용해 mask 영역의 픽셀만 3D point로 변환한다.

핵심 수식은 pinhole camera model 기반 역투영이다.

```text
X_camera = depth * inv(K) * [u, v, 1]^T
X_world  = R * X_camera + t
```

이 단계부터 수업에서 배운 camera geometry가 직접 쓰인다.

### T5. Object Point Cloud Fusion

여러 frame에서 얻은 객체 point cloud를 하나로 합친다.

이때 pose, scale, outlier 문제가 드러난다.

처음에는 2개 frame만 fusion하는 것을 목표로 한다.

### T6. Object Prior Fitting

fused object cloud에서 객체의 중심, 방향, 크기, bounding box를 추정한다.

초기에는 PCA 기반 oriented bounding box 또는 Open3D bounding box를 사용할 수 있다.

출력은 후속 평가와 시각화가 사용할 `ObjectPrior`다.

### T7. Evaluation

수동 실측값과 예측값을 비교한다.

초기 metric은 단순하게 시작한다.

```text
absolute_error_cm
relative_error_percent
```

중요한 것은 정확도를 과장하지 않는 것이다.

실측값이 없으면 정확도를 주장하지 않는다.

### T8. Visualization

Open3D 또는 Rerun으로 결과를 시각화한다.

최소한 아래가 보여야 한다.

- raw frame
- mask overlay
- camera trajectory
- per-frame point cloud
- fused object cloud
- oriented bounding box
- dimension label
- confidence 또는 실패 이유

## 예상 코드 구조

최종적으로는 대략 이런 구조를 목표로 한다.

```text
src/object3d/
  capture/
  adapters/
    segmentation/
    geometry/
  geometry/
  reconstruction/
  priors/
  evaluation/
  visualization/
  pipeline/

configs/
  default.yaml
  capture.yaml
  models/
    segmentation.yaml
    geometry.yaml

tests/
  capture/
  adapters/
  geometry/
  reconstruction/
  priors/
  evaluation/
  visualization/

docs/
  README.md
```

## 현재 구현 상태

현재 T1 capture 작업이 진행 중이다.

현재 또는 직전 PR 기준으로 다음 코드가 준비되고 있다.

```text
src/object3d/capture/
  records.py
  sampling.py
  frame_source.py
  image_io.py
  manifest.py
  pipeline.py
```

T1의 목표는 아래와 같다.

- 입력 영상 또는 합성 frame source를 공통 인터페이스로 다룬다.
- 원하는 target fps에 맞게 frame을 샘플링한다.
- 샘플링된 frame을 이미지로 저장한다.
- downstream이 사용할 manifest JSON을 만든다.
- 수동 실측값과 촬영 메타데이터를 기록한다.

아직 부족한 점은 다음과 같다.

- 사용자가 바로 실행할 수 있는 CLI 또는 `main.py` 진입점이 없다.
- config-driven 실행 로더가 없다.
- 실제 스마트폰 영상에 대한 검증이 부족하다.
- non-integer FPS와 unknown frame count 처리 개선이 필요하다.

## 중요한 설계 원칙

### 1. 처음부터 방 전체를 복원하지 않는다

방 전체 복원은 어렵고 비용이 크다.

첫 목표는 단일 객체다.

단일 객체가 안정적으로 동작해야 방 전체나 scene-level completion으로 확장할 수 있다.

### 2. 모델 출력은 정답이 아니라 noisy measurement다

SAM mask, depth, pose, point cloud는 모두 오차가 있다.

따라서 결과를 그대로 믿지 않고 confidence, filtering, sanity check를 둔다.

### 3. raw model output을 downstream에 직접 흘리지 않는다

모든 외부 모델 출력은 adapter를 통해 표준 record로 변환한다.

이렇게 해야 나중에 SAM, SAM2, GroundingDINO, MapAnything, VGGT, COLMAP을 바꿔도 전체 파이프라인이 무너지지 않는다.

### 4. 정확도 주장은 실측값이 있을 때만 한다

수동 측정값 없이 "정확하다"고 말하지 않는다.

초기 평가는 물리 치수 비교부터 시작한다.

### 5. 자동화는 필요해질 때 추가한다

이 프로젝트에서는 이전에 `.claude/agents`, `.claude/skills`, `.claude/rules` 기반의 큰 하네스를 한 번 구성했다.

하지만 초기 MVP 단계에서는 그 구조가 너무 무거웠다.

앞으로는 기본 작업을 `docs/` 중심으로 가볍게 진행한다.

반복되는 고통이 실제로 확인되면 그때 필요한 자동화만 추가한다.

## Claude/Codex 에이전트 작업 원칙

새 에이전트는 기본적으로 이 문서부터 읽는다.

처음부터 `.claude/` 전체를 읽지 않는다.

작업 전에는 아래를 확인한다.

```text
1. 지금 목표가 무엇인가?
2. 어떤 단계(T1~T8)에 해당하는가?
3. 수정 가능한 파일 범위는 어디인가?
4. 이번 작업에서 하지 않을 것은 무엇인가?
5. 어떻게 검증할 것인가?
```

작업할 때는 다음을 지킨다.

- 작은 단위로 구현한다.
- 기존 파일 구조를 먼저 확인한다.
- 테스트 또는 시각 검증이 가능한 단위로 끝낸다.
- 수업 자료나 reference 원본은 git에 추가하지 않는다.
- raw data, checkpoints, large artifacts는 git에 추가하지 않는다.
- 불확실한 설계 선택은 바로 결정하지 말고 선택지로 올린다.

## 다음에 할 일

현재 우선순위는 다음과 같다.

1. T1 capture PR의 리뷰 피드백 반영
   - non-integer FPS sampling 개선
   - unknown frame count 처리 개선
   - 사용자가 실행할 수 있는 최소 CLI 또는 실행 예시 검토
2. T1 capture를 안정화한 뒤 T2 segmentation adapter 설계
3. T3 geometry adapter는 실모델보다 generic contract와 mock 우선
4. T4 back-projection부터 수업의 camera geometry 개념을 본격 적용

## 프로젝트에서 하지 말아야 할 것

- 첫 기능부터 방 전체 복원을 시도하지 않는다.
- 첫 MVP 전에 대규모 모델 학습을 시작하지 않는다.
- 실모델 연동 전에 downstream contract를 불안정하게 만들지 않는다.
- raw data나 checkpoint를 git에 넣지 않는다.
- `.claude/` 하네스를 기본 작업마다 무조건 읽지 않는다.
- 문서 구조를 먼저 키운 뒤 구현을 따라오게 하지 않는다.

## 참고 키워드

- SAM / SAM2
- Segment Anything
- Object Prior
- Masked Back-Projection
- Camera Intrinsics
- Camera Pose
- Depth Map
- Point Cloud
- Oriented Bounding Box
- Open3D
- Rerun
- MapAnything
- VGGT
- COLMAP
- No-Training MVP
- Context Engineering
- Harness Engineering
