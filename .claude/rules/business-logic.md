# 비즈니스 로직 및 도메인 규칙

이 파일은 프로젝트가 무엇을 만들고 무엇을 과장하지 말아야 하는지 정한다.

## 핵심 제품 정의

이 프로젝트는 SAM 계열 모델의 2D mask/tracking 결과를 3D object prior로 변환해 객체 추적, 크기 측정, 방향 추정, confidence, 배치 가능성 판단을 수행한다.

## MVP 규칙

- 첫 목표는 방 전체 3D 복원이 아니다.
- 첫 목표는 단일 객체를 안정적으로 추적하고 측정하는 것이다.
- 첫 객체는 박스, 책, 단순 의자처럼 형태가 단순하고 반사가 적은 물체를 우선한다.
- 정확도 주장은 수동 실측값과 비교할 수 있을 때만 한다.
- 배치 가능성은 rough feasibility로 표현한다. 정밀 AR 배치처럼 과장하지 않는다.

## 모델 사용 규칙

- SAM/SAM2 output은 mask evidence이지 semantic truth가 아니다.
- MapAnything/VGGT/COLMAP output은 noisy measurement로 취급한다.
- COLMAP과 learned geometry의 scale convention이 같다고 가정하지 않는다.
- Seen2Scene은 full reproduction 대상이 아니라 visibility reasoning 참고 자료다.

## 학습 전략 규칙

- 처음부터 dataset fine-tuning을 시작하지 않는다.
- 먼저 no-training MVP를 완성한다.
- 그 다음 mask threshold, frame filtering, outlier removal, bbox fitting, scale alignment를 튜닝한다.
- 반복 실패가 여러 scene에서 확인된 뒤에만 좁은 병목 하나를 학습 후보로 선택한다.

## 사용자에게 보여줄 결과

최소 결과는 다음 질문에 답해야 한다.

- 객체가 3D 공간에서 어디에 있는가?
- width, depth, height는 얼마인가?
- 방향은 어떻게 놓여 있는가?
- confidence는 어느 정도인가?
- 어떤 표면 또는 시야가 부족한가?
- 목표 공간에 배치 가능한가?

## 멈출 조건

- mask overlay가 틀렸는데 geometry로 넘어가려 한다.
- one-frame point cloud가 틀렸는데 multi-frame fusion을 하려 한다.
- confidence 없이 치수를 표시하려 한다.
- 수동 측정값 없이 정확도를 주장하려 한다.
- 실패 frame을 숨기고 성공 frame만 보여주려 한다.

## 안티패턴

`anti-pattern-check` 스킬이 구현·리뷰 전에 확인하는 프로젝트 전역 금지 목록이다.

### 전역

- 프로젝트 폴더 전체를 한 번에 읽지 않는다.
- `cv_tutorial/` 전체를 훑는 식으로 컨텍스트를 낭비하지 않는다.
- 단일 객체 MVP가 없는데 방 전체 dense reconstruction부터 시작하지 않는다.
- Seen2Scene 전체 재현을 첫 목표로 삼지 않는다.
- 대규모 dataset 또는 checkpoint를 먼저 내려받지 않는다.
- pretrained model output을 ground truth로 취급하지 않는다.
- 실패 사례를 보고서에서 숨기지 않는다.
- raw video, checkpoint, cache, secret을 커밋하지 않는다.

### Segmentation

- mask overlay를 확인하지 않고 geometry 단계로 넘기지 않는다.
- frame마다 object id가 바뀌는 상태를 허용하지 않는다.
- confidence 또는 mask area anomaly를 기록하지 않고 threshold를 고정하지 않는다.
- SAM 결과가 곧 semantic label이라고 가정하지 않는다.

### Geometry

- camera intrinsics, depth scale, pose convention을 확인하지 않고 fusion하지 않는다.
- 여러 frame fusion부터 시작하지 않는다. one-frame point cloud부터 확인한다.
- COLMAP scale과 learned model scale이 같다고 가정하지 않는다.
- lens distortion 가능성을 무시하지 않는다.

### Reconstruction

- background가 섞인 mask point를 그대로 object cloud로 쓰지 않는다.
- outlier filtering 없이 bounding box를 fitting하지 않는다.
- point cloud density를 확인하지 않고 measurement 결과를 믿지 않는다.

### Object prior

- oriented bounding box axis convention을 기록하지 않고 dimension을 보고하지 않는다.
- 수동 측정값 없이 정확도를 주장하지 않는다.
- under-observed surface를 "완성된 표면"처럼 표시하지 않는다.
- placement feasibility를 정밀 AR 배치처럼 과장하지 않는다.

### Evaluation

- 시각적으로 좋아 보인다는 말만 남기지 않는다.
- parameter search 기록 없이 결과만 남기지 않는다.
- 실패 frame을 제외하고 성공 frame만 보여주지 않는다.

### Review와 Git

- 리뷰 finding을 local chat에만 남기지 않는다. PR이 있으면 PR comment로 남긴다.
- 사용자 승인 없이 destructive git command를 실행하지 않는다.
- unrelated file을 함께 staging하지 않는다.
- GitHub에 보이는 커밋·PR·리뷰 comment를 영어로 작성하지 않는다. 기술 식별자만 예외다.
