# 첫 No-Training MVP 상세 계획

> 에이전트 작업자용: 이 계획은 checkbox 단위로 실행한다. 구현 전 `superpowers:using-superpowers`, `superpowers:writing-plans`, project routing 문서를 확인한다.

**목표:** 스마트폰 영상 속 단일 객체를 추적하고, mask와 depth/pose를 결합해 3D object prior를 생성하는 첫 MVP를 만든다.

**아키텍처:** 입력 영상에서 frame을 추출하고, SAM 계열 모델로 객체 mask/tracking을 만든다. 이후 geometry adapter가 제공하는 depth/pose와 mask를 결합해 object point cloud를 만들고, oriented bounding box와 치수를 추정한다.

**기술 스택:** Python, OpenCV, NumPy, Open3D, Rerun, SAM/SAM2 계열 adapter, MapAnything 또는 VGGT adapter, 선택적으로 COLMAP.

## 파일 구조

- 생성:
  - `configs/default.yaml`
  - `configs/models/segmentation.yaml`
  - `configs/models/geometry.yaml`
  - `src/object3d/capture/`
  - `src/object3d/adapters/`
  - `src/object3d/geometry/`
  - `src/object3d/reconstruction/`
  - `src/object3d/priors/`
  - `src/object3d/evaluation/`
  - `src/object3d/visualization/`
- 수정:
  - `../../../README.md`
  - `../../../src/README.md`
- 테스트:
  - `tests/`
- 산출물:
  - mask overlay image
  - one-frame object point cloud
  - fused object point cloud
  - object prior report

## 사전 조건

- 첫 객체는 박스, 책, 단순 의자처럼 반사가 적고 형태가 단순해야 한다.
- 수동 실측값 `width`, `depth`, `height`를 cm 단위로 기록해야 한다.
- geometry model은 MapAnything 또는 VGGT 중 하나만 먼저 선택한다.
- 대규모 dataset, checkpoint, fine-tuning은 이 단계에서 시작하지 않는다.

## 작업 단계

- [ ] Step 1: 첫 실험 객체와 촬영 조건을 확정한다.
  - 파일: `configs/default.yaml`
  - 검증: 객체 이름, 실측값, camera mode, frame sampling rate가 기록되어야 한다.
  - 기대 결과: 재촬영 없이 같은 입력을 다시 처리할 수 있다.

- [ ] Step 2: frame sampling 흐름을 만든다.
  - 파일: `src/object3d/capture/`
  - 검증: 입력 영상에서 일정한 간격의 frame manifest가 생성되어야 한다.
  - 기대 결과: frame id와 image path가 안정적으로 연결된다.

- [ ] Step 3: segmentation adapter contract를 만든다.
  - 파일: `src/object3d/adapters/`
  - 검증: frame id, object id, binary mask, confidence, prompt type을 저장해야 한다.
  - 기대 결과: raw model output이 downstream으로 직접 새지 않는다.

- [ ] Step 4: mask overlay를 먼저 확인한다.
  - 파일: `src/object3d/visualization/`
  - 검증: 대표 frame 위에 mask가 보이는 image artifact가 생성되어야 한다.
  - 기대 결과: mask가 floor, wall, 다른 객체를 크게 포함하면 geometry로 넘어가지 않는다.

- [ ] Step 5: geometry adapter contract를 만든다.
  - 파일: `src/object3d/adapters/`
  - 검증: depth, intrinsics, pose, coordinate convention이 기록되어야 한다.
  - 기대 결과: scale과 pose convention을 모르는 상태로 back-projection하지 않는다.

- [ ] Step 6: 한 frame의 masked pixel만 3D point로 역투영한다.
  - 파일: `src/object3d/geometry/`
  - 검증: one-frame object point cloud를 Open3D 또는 Rerun으로 확인한다.
  - 기대 결과: object cloud가 대략적인 객체 형태를 가진다.

- [ ] Step 7: 두 frame만 fusion한다.
  - 파일: `src/object3d/reconstruction/`
  - 검증: 두 frame의 point가 서로 크게 어긋나지 않아야 한다.
  - 기대 결과: pose/scale 문제가 있으면 multi-frame fusion 전에 멈춘다.

- [ ] Step 8: object prior를 fitting한다.
  - 파일: `src/object3d/priors/`
  - 검증: oriented bounding box, center, width/depth/height, confidence가 계산되어야 한다.
  - 기대 결과: 축 convention과 단위가 report에 함께 남는다.

- [ ] Step 9: 수동 실측값과 비교한다.
  - 파일: `src/object3d/evaluation/`
  - 검증: 절대 오차 cm와 상대 오차 percent가 기록되어야 한다.
  - 기대 결과: 오차가 크면 mask, depth, pose, outlier 중 어느 계층 문제인지 분리한다.

- [ ] Step 10: MVP 결과를 시각화한다.
  - 파일: `src/object3d/visualization/`
  - 검증: raw frame, mask overlay, camera trajectory, object point cloud, 3D bbox가 보인다.
  - 기대 결과: 사용자가 log 없이도 결과와 실패 이유를 이해할 수 있다.

## 검증

- unit test: schema 변환, back-projection 수식, bbox dimension 계산
- smoke test: 한 영상에서 frame sampling부터 object prior report까지 실행
- visual check: mask overlay, one-frame point cloud, fused point cloud, bbox view
- metric: `absolute_error_cm`, `relative_error_percent`

## 실패 조건

- mask가 객체보다 배경을 더 많이 포함한다.
- one-frame point cloud가 형태를 알아볼 수 없다.
- two-frame fusion에서 객체가 두 겹으로 보인다.
- 수동 실측값 없이 정확도를 주장해야 하는 상황이 생긴다.
- confidence 없이 치수를 표시한다.

실패가 non-obvious하면 `.claude/failures/`에 failure note를 남긴다.

## 커밋 후보

```text
feat(#issue): 첫 객체 3D prior MVP 파이프라인 추가
```

## 라우팅·작업 분해 기록 (2026-05-21)

`/superpowers:writing-plans` dry-run 요청으로 수행한 No-Training MVP 작업 분해다. **코드·Issue·worktree는 아직 생성하지 않았다.** 아래 미해결 결정 3건이 확정되기 전까지 T3·T8 worker brief는 초안 상태로 둔다.

### 라우팅

- 분류: "작업 분해" / 계획 요청 — 파이프라인 코드를 직접 만들지 않으므로 router 키워드 우선순위 #3(구현 흐름) 대신 분류표로 라우팅.
- 주 담당: **Orchestrator Agent** (메인 세션) — 작업 분해와 멀티에이전트 조율 소유.
- 지원: Issue Manager(Issue draft, task↔issue 매핑), Git Manager(worktree·branch stack), Research + Integration(계획 정합성).
- 미래 worker owner: Data Capture / Segmentation / Geometry / Reconstruction / Object Prior / Evaluation / Visualization.
- 핵심 skill: task-orchestration, issue-worktree-workflow, implementation-planning, anti-pattern-check, decision-brief.

### 8개 작업 ↔ 기존 10단계 매핑

| 작업 | 내용 | 기존 Step | 주 담당 |
|---|---|---|---|
| T1 | 입력 영상/프레임 샘플링 | Step 1+2 | Data and Capture Agent |
| T2 | SAM/SAM2 segmentation adapter | Step 3 (+ Step 4 mask overlay 슬라이스) | Segmentation Agent |
| T3 | depth/pose adapter (mock/interface) | Step 5 | Geometry Agent |
| T4 | masked back-projection | Step 6 | Geometry Agent |
| T5 | object point cloud fusion | Step 7 | Reconstruction Agent |
| T6 | oriented bbox 및 크기 측정 | Step 8 | Object Prior Agent |
| T7 | evaluation log | Step 9 | Evaluation Agent |
| T8 | Open3D/Rerun visualization | Step 4 + Step 10 | Visualization Agent |

### 작업별 write scope (상호 비중첩)

| 작업 | 작성 가능 범위 |
|---|---|
| T1 | `src/object3d/capture/**`, `configs/capture.yaml`, `configs/default.yaml`(생성), `tests/capture/**` |
| T2 | `src/object3d/adapters/segmentation/**`, `configs/models/segmentation.yaml`, `tests/adapters/segmentation/**` |
| T3 | `src/object3d/adapters/geometry/**`, `configs/models/geometry.yaml`, `tests/adapters/geometry/**` |
| T4 | `src/object3d/geometry/**`, `tests/geometry/**` |
| T5 | `src/object3d/reconstruction/**`, `tests/reconstruction/**` |
| T6 | `src/object3d/priors/**`, `tests/priors/**` |
| T7 | `src/object3d/evaluation/**`, `docs/experiment_log.md`, `tests/evaluation/**` |
| T8 | `src/object3d/visualization/**`, `apps/**`, `tests/visualization/**` |

공유 파일 규칙: `configs/default.yaml`은 T1이 생성·고정하고 이후 작업은 자기 모듈 config 파일만 추가한다. root `README.md`/`src/README.md`는 T8(통합 시점)에서 한 번만 갱신한다.

### 의존 그래프

```text
T1 ──┬─> T2 ──┬─────────────> T8(mask overlay 슬라이스)
     └─> T3 ──┤
              └─> T4 ─> T5 ─> T6 ─> T7 ─> T8(최종 데모)
```

T2 ∥ T3 병렬 가능. T4는 T2·T3 둘 다 필요.

### stacked branch 안

```text
main
 └ feat/1-capture
    ├ feat/2-segmentation-adapter
    └ feat/3-geometry-adapter
       └ feat/4-masked-backprojection   (T2·T3 위에 rebase)
          └ feat/5-pointcloud-fusion
             └ feat/6-oriented-bbox
                └ feat/7-evaluation-log
                   └ feat/8-visualization
```

### 확정된 결정 (2026-05-21)

1. **Geometry adapter(T3) 범위** — interface + mock 우선. generic `GeometryRecord` contract와 합성 depth/pose mock을 먼저 만들어 T4~T7 downstream을 검증한다. 실모델(MapAnything·VGGT) 연동은 contract 안정 후 별도 후속 작업(T3-follow)으로 분리한다.
2. **Mask overlay 소유** — Segmentation Agent가 소유. T2가 자기 모듈(`adapters/segmentation/**`) 안에 thin overlay util을 두고 mask 검증 게이트 이미지를 생성한다. T8 Visualization은 최종 데모 단일 owner로 유지하고 작업은 8개를 유지한다.
3. **첫 geometry 모델 경로** — 미정. 특정 모델에 묶이지 않는 generic contract로 설계하고 모델 선정은 다음 라운드에서 Research Agent가 맡는다.

### 다음 명령 예시

- 결정 확정: "geometry는 interface+mock, mask overlay는 segmentation 소유, 모델 경로는 미정으로 가자"
- 실행 착수: "T1 capture부터 Issue 만들고 worktree 잡아서 시작해줘"
- 한 작업만: "T1 입력/프레임 샘플링 작업 폴더랑 worker brief 확정해줘"
