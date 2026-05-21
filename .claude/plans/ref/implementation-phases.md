# 세부 구현 단계

이 파일은 [implementation-strategy.md](../implementation-strategy.md)를 읽은 뒤, 실제 단계별 구현 세부가 필요할 때만 연다.

## Phase 0: 연구와 환경 결정

모든 모델을 먼저 설치하지 않는다. segmentation 경로 1개와 geometry 경로 1개를 먼저 고른다.

권장 첫 stack:

- segmentation: SAM 2 video tracking
- geometry: MapAnything 또는 VGGT
- fallback geometry: COLMAP + monocular depth
- 첫 객체: 종이 박스, 단순한 의자, 작은 테이블, 모니터, 캐리어

처음부터 피할 대상:

- 유리
- 거울
- 투명 물체
- 반사가 강한 검은 물체
- 얇은 케이블
- 다리가 너무 얇은 의자

기대 산출물:

- `configs/default.yaml`
- `configs/models/*.yaml`
- `data/raw/videos/<scene_name>.mp4`
- `docs/experiment_log.md`

## Phase 1: 단일 객체 Segmentation과 Tracking

mask가 안정되기 전에는 3D로 넘어가지 않는다.

구현 흐름:

1. 일정한 간격으로 keyframe을 추출한다.
2. 첫 프레임에서 객체를 prompt한다.
3. mask를 이후 프레임으로 전파한다.
4. raw mask, filtered mask, confidence를 저장한다.
5. mask가 깨진 프레임은 제외한다.

성공 기준:

- 최소 20개 usable frame에서 같은 object ID가 유지된다.
- mask overlay를 눈으로 확인할 수 있다.
- 실패 사례가 기록되어 있다.

기록할 실패:

- mask가 floor나 wall을 객체에 포함한다.
- mask가 다른 객체로 전환된다.
- occlusion 중 mask가 사라진다.
- 객체 경계가 너무 많이 깜빡인다.

## Phase 2: Depth, Pose, Back-Projection

1프레임과 2프레임 geometry를 검증하기 전에 전체 프레임을 fusion하지 않는다.

구현 흐름:

1. 선택된 frame에 geometry model을 실행한다.
2. depth, camera intrinsics, camera pose를 저장한다.
3. 아래 식으로 역투영한다.

```text
X_camera = depth(u, v) * inverse(K) * [u, v, 1]^T
X_world = R * X_camera + t
```

4. mask를 적용해 object point만 남긴다.
5. frame별 object cloud와 fused object cloud를 저장한다.

성공 기준:

- object cloud가 알아볼 수 있는 형태를 가진다.
- 인접 frame의 point가 겹친다.
- outlier removal이 시각 품질을 개선한다.

## Phase 3: Object Prior 추정

confidence와 축 convention 없이 정밀 치수를 보고하지 않는다.

추정 항목:

- axis-aligned bounding box
- oriented bounding box
- center point
- width, depth, height
- PCA 기반 dominant orientation
- floor 또는 support-plane 접촉 여부
- reconstruction confidence

성공 기준:

- 치수가 수동 실측값과 비교된다.
- orientation이 시각적으로 납득 가능하다.
- mask 품질이 낮거나 view가 부족하면 confidence가 내려간다.

## Phase 4: 평가와 데이터 분석

pipeline 결정을 바꾸지 않는 장식성 분석은 추가하지 않는다.

필수 metric:

```text
absolute_error_cm = abs(predicted_cm - measured_cm)
relative_error_percent = absolute_error_cm / measured_cm * 100
```

필수 비교:

- mask confidence filtering 적용 전/후
- point cloud outlier removal 적용 전/후
- axis-aligned box와 oriented box
- 선택 사항: learned geometry와 COLMAP baseline

## Phase 5: 실용 기능

단일 객체 report가 안정되기 전에 넓은 app을 만들지 않는다.

권장 출력 예시:

```text
객체: 의자
추정 크기: W 48.2 cm, D 52.6 cm, H 81.4 cm
신뢰도: 중상
배치 판단: 목표 공간에 배치 가능, 측면 여유 7.1 cm
촬영 가이드: 뒤쪽 왼편 관측이 부족함
```

성공 기준:

- 사용자가 log를 보지 않고도 결과를 이해한다.
- uncertainty가 표시된다.
- 실패 이유가 표시된다.

## Phase 6: 튜닝과 가벼운 학습 검토

MVP가 안정되기 전에는 학습이나 fine-tuning을 시작하지 않는다.

먼저 할 일:

1. mask confidence threshold를 조정한다.
2. frame filtering 기준을 조정한다.
3. point cloud outlier removal 기준을 조정한다.
4. bbox fitting 방식을 비교한다.
5. depth/pose scale alignment를 점검한다.

그 다음에만 dataset 기반 조정을 검토한다.

학습 후보는 하나의 병목으로 제한한다.

- mask refinement
- depth correction
- confidence calibration
- object dimension regression
- lightweight 2.5D depth completion

시작 조건:

- 같은 실패 유형이 여러 scene에서 반복된다.
- rule-based tuning으로 개선이 멈췄다.
- 입력/출력 schema와 metric이 고정되어 있다.
- dataset 수집 비용과 GPU 시간이 감당 가능하다.

하지 말 것:

- full 3D scene completion model을 처음부터 학습하지 않는다.
- 학습을 pipeline 검증의 대체물로 쓰지 않는다.
- 정확한 ground truth 없이 성능 향상을 주장하지 않는다.

## 확장 후보

MVP가 동작하기 전에는 확장을 고르지 않는다.

가능한 확장:

- multi-object tracking and measurement
- Grounded SAM 또는 SAM 3 기반 text-prompt discovery
- visibility-aware capture guidance
- floor, wall, tabletop plane fitting
- 간단한 furniture replacement demo
- object-level TSDF
- lightweight 2.5D depth completion
