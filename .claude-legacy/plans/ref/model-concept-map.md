# 모델과 개념 지도

이 파일은 모델 설명, 공부할 개념, 논문/자료 연결이 필요할 때만 연다. 구현 중에는 필요한 section만 읽는다.

## 프로젝트 핵심 해석

이 프로젝트의 주제는 최신 SAM 계열 모델을 2D segmentation 도구로만 쓰는 것이 아니다. SAM의 mask, tracking, prompt, confidence를 3D 공간의 object prior로 바꿔 객체 추적, 측정, 배치 판단에 활용한다.

## 모델별 역할

| 모델/도구 | 역할 | 이 프로젝트에서 쓰는 방식 |
|---|---|---|
| SAM 계열 | 객체 mask와 prompt 기반 분리 | 목표 객체의 frame별 binary mask와 confidence 생성 |
| SAM 2 | video object tracking | 같은 객체 id를 프레임 사이에서 유지 |
| GroundingDINO/Grounded SAM 계열 | text-prompt object discovery | “의자”, “박스” 같은 텍스트로 후보 객체 찾기 |
| MapAnything | feed-forward metric 3D geometry | depth, camera pose, metric geometry 후보 생성 |
| VGGT | visual geometry foundation model | depth/pose/point map 후보 생성 또는 비교 |
| COLMAP | 전통 SfM/MVS baseline | learned geometry와 pose/scale sanity check 비교 |
| Seen2Scene | visibility-guided 3D completion 참고 논문 | full reproduction이 아니라 observed/unobserved 사고방식만 차용 |

## 공부할 개념 우선순위

1. Camera geometry: pinhole camera, intrinsics, extrinsics, projection/back-projection
2. Multi-view geometry: epipolar geometry, triangulation, PnP, bundle adjustment
3. Segmentation: binary mask, instance consistency, promptable segmentation, tracking drift
4. 3D representation: point cloud, voxel, TSDF, SDF, occupancy
5. Object prior: oriented bounding box, PCA orientation, support plane, confidence
6. Evaluation: 수동 실측값, absolute/relative error, ablation, failure case
7. Visibility reasoning: observed, empty, unobserved 영역 구분

## 처음부터 깊게 들어가지 말 것

- Seen2Scene의 full flow matching 학습
- 대규모 3D dataset 전처리
- 방 전체 mesh reconstruction
- NeRF 또는 3D Gaussian Splatting 중심 프로젝트 전환
- 정밀 AR 수준의 배치 정확도 주장

## 수업 자료 연결

- 영상 처리 기초: mask 전처리, threshold, morphology, edge/contour 확인
- 카메라 모델: depth pixel을 3D point로 back-project
- correspondence와 geometry: COLMAP baseline, pose sanity check
- segmentation/CNN: SAM 계열을 이해하기 위한 foundation
- 3D vision: point cloud, fusion, TSDF와 visibility 개념 연결

## 지식 베이스 기록 규칙

새 개념을 공부하거나 실험에서 자주 헷갈린 개념이 나오면 먼저 사용자에게 저장 형식을 확인한다. 기본 후보는 다음 세 가지다.

1. 이 프로젝트 안의 `plans/ref/`에 짧은 개념 note로 저장
2. 별도 wiki 또는 Notion에 장기 학습 note로 저장
3. 실패나 삽질이면 `.claude/failures/`에 failure note로 저장

한 문서는 하나의 개념만 다룬다. 논문 요약, 구현 적용, 실패 사례를 한 파일에 과하게 섞지 않는다.
