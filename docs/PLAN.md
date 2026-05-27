# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. PR 설명은 어려운 용어를 풀어서 쓴다.

## 진행상황 기록 위치

현재 진행상황은 이 문서(`docs/PLAN.md`)에 요약한다.

상세 설명과 검증 기록은 아래 문서로 분리한다.

- 프로젝트 목적/서비스 설명: `docs/README.md`
- 실제 사진 SAM2 검증 상세: `docs/validation/20260524-real-photo-sam2-object-prior.md`
- PR에서 바로 볼 검증 이미지: `docs/validation/assets/20260524-real-photo-sam2-overlay-contact-sheet.jpg`
- 대표 fixture file geometry smoke 이미지: `docs/validation/assets/20260526-representative-fixture-geometry-smoke.jpg`
- geometry backend 후보 조사: `docs/research/20260526-geometry-backend-candidates.md`
- VGGT 실행 환경 runbook: `docs/runbooks/20260526-vggt-runtime-environments.md`
- VGGT smoke 실수 기록: `docs/runbooks/20260526-vggt-smoke-troubleshooting.md`
- 일반 객체 SAM2 -> 3D cleanup runbook: `docs/runbooks/20260526-general-sam2-3d-cleanup.md`
- 방 영상 촬영 guide: `docs/runbooks/20260527-room-video-capture-guide.md`
- 기말 프로젝트 구현 계획: `docs/superpowers/plans/2026-05-27-room-object-3d-prior-final-project.md`
- 기말 프로젝트 scope 실수 방지 기록: `docs/solutions/workflow-issues/scope-final-project-to-coarse-room-object-priors.md`
- 실제 노트북 VGGT MPS smoke 검증: `docs/validation/20260526-real-laptop-vggt-mps-smoke.md`
- 실제 노트북 SAM2 + VGGT mask smoke 검증: `docs/validation/20260526-real-laptop-sam2-vggt-mask-smoke.md`
- 실제 노트북 point cloud outlier filter smoke 검증: `docs/validation/20260526-real-laptop-outlier-filter-smoke.md`
- 실제 노트북 multi-view VGGT validation: `docs/validation/20260526-real-laptop-multiview-vggt-validation.md`
- 일반 객체 SAM2 -> 3D cleanup smoke: `docs/validation/20260526-general-sam2-3d-cleanup-smoke.md`

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- `prior_from_mask` CLI는 segmentation 결과를 3D point cloud, bbox, scene manifest로 바꿀 수 있다.
- `prior_from_mask` CLI는 고정 mock depth뿐 아니라 `.npz` file geometry 입력도 받을 수 있다.
- scene manifest는 summary backend와 Rerun lazy backend로 열 수 있다.
- Rerun backend는 `.rrd` recording 파일로 3D 장면을 저장할 수 있다.
- 실제 SAM2 checkpoint를 사용해 synthetic image와 실제 사용자 사진 모두에서 smoke 검증을 수행했다.
- 실제 사진 3장, 물체 후보 9개를 대상으로 성공/주의/실패 케이스를 분리해 기록했다.
- 노트북, 영수증, 태블릿+키보드는 원본 개인 사진 없이 재현 가능한 synthetic smoke fixture로 고정했다.
- 대표 synthetic smoke fixture는 각 case별 `geometry.npz`도 함께 생성해 file geometry 경로까지 회귀 테스트할 수 있다.
- VGGT, MapAnything, COLMAP을 비교했고 다음 실제 geometry adapter 1순위는 VGGT로 정했다.
- VGGT prediction을 표준 `.npz` geometry contract로 저장하는 adapter skeleton이 있다.
- 로컬 MacBook Pro M5/MPS와 학교 NVIDIA RTX 30/40 series CUDA 환경을 나눠 실제 VGGT smoke 준비 절차를 문서화했다.
- `vggt_geometry` CLI skeleton은 이미지 입력을 받아 VGGT prediction을 `geometry.npz`로 저장하는 경로를 갖는다.
- 기본 테스트는 injected fake runner로 통과하므로, VGGT checkpoint가 없어도 test suite가 깨지지 않는다.
- 실제 노트북 사진 1장으로 Mac MPS VGGT checkpoint smoke가 `geometry.npz -> prior_from_mask -> Rerun .rrd`까지 성공했다.
- mask/depth shape mismatch, macOS image permission, Rerun viewer PATH 문제는 코드와 runbook에 반영했다.
- 같은 노트북 사진에 SAM2 mask를 적용해 manual box보다 effective point count를 26.5% 줄였다.
- SAM2 + VGGT point cloud에 radial percentile outlier filter를 적용해 bbox 최대 축을 31.2% 줄였다.
- 노트북 사진 5장 few-view VGGT validation을 수행했고, per-view 3D prior는 생성되지만 view별 bbox 치수가 크게 흔들리는 것을 확인했다.
- SAM2 mask를 3D로 올리기 전에 largest component cleanup과 optional erosion을 적용하는 일반 객체용 cleanup 옵션을 추가했다.
- PR A / 이슈 #60 범위로 방 영상 keyframe 추출 CLI와 keyframe manifest 기반 VGGT batch geometry CLI를 추가했다.

## 현재 단계

현재는 **No-Training MVP의 end-to-end skeleton이 연결된 상태**다.

쉽게 말하면, 아래 흐름은 이미 한 번씩 코드와 smoke test로 확인했다.

```text
이미지/영상 입력
  -> frame 또는 image 단위 입력 준비
  -> SAM2/manual segmentation
  -> mask.npy / overlay.png / summary.json
  -> mock depth 또는 file geometry 기반 masked back-projection
  -> object point cloud
  -> oriented bbox
  -> scene manifest
  -> Rerun .rrd 저장
```

다만 아직 **실제 3D 정확도 검증 단계는 아니다.**

현재 `prior_from_mask`는 기본값으로 `--depth-m 2.0` 같은 고정 mock depth를 사용한다. 필요하면 `--geometry-npz`로 외부 depth/pose 산출물을 넣을 수 있고, Mac MPS에서 VGGT 단일 이미지 산출물을 이 경로에 실제로 연결해 봤다. 또한 optional point cloud outlier filter로 bbox를 끌고 가는 꼬리 점을 일부 줄일 수 있다. 다만 단일 이미지 depth와 scale 검증 전 단계라서 지금 만들어지는 3D bbox 크기 값은 아직 실제 물체 치수로 보지 않는다. 현재 의미는 **실제 VGGT geometry가 3D prior 파이프라인 끝까지 연결되는지 보는 구조 검증 값**이다.

## 기말 프로젝트 제출 방향

이슈 #58 기준으로, 2주 남은 기말 대체 텀프로젝트 방향은 **작은 정적 실내 공간 동영상에서 coarse room context와 object-level 3D prior를 만드는 것**으로 고정한다.

목표를 아래 세 가지까지만 둔다.

1. **방 전체 sparse/dense-ish point cloud**
   - 완전한 textured mesh가 아니라, 선택 keyframe의 VGGT depth/pose를 이용한 coarse room point cloud다.
2. **바닥/벽/책상 plane 대략 추정**
   - semantic label을 자동 확정하지 않고, rough plane candidates와 시각적/수치적 근거를 보여준다.
3. **물체별 3D bbox 추정**
   - SAM2/manual mask로 선택한 2-3개 물체를 world-space point cloud로 올리고, frame 간 fusion 뒤 bbox와 실측 오차를 비교한다.

명시적으로 하지 않는 것:

- 방 전체를 깔끔한 3D mesh로 복원한다고 주장하지 않는다.
- 대규모 scene completion이나 학습 기반 3D generative model을 붙이지 않는다.
- 투명 컵/얇은 물체/반사 화면을 필수 성공 기준으로 두지 않는다.

실행 단위는 다음 T 순서로 나눈다.

- T21: video keyframe extraction
- T22: VGGT batch geometry from keyframes
- T23: keyframe object segmentation batch
- T24: object-aware multi-view fusion
- T25: coarse room point cloud + rough plane summary
- T26: measurement evaluation + final smoke report

## 작업 범위

최근 PR 범위:

- PR #31: synthetic image 기반 SAM2 -> 3D prior -> Rerun recording 검증
- PR #32: 실제 사용자 사진 3장/9개 물체 후보 기반 SAM2 -> 3D prior 검증 문서화
- PR #35: 대표 smoke fixture 생성기 추가
- PR #37 / #36: 실제 depth/pose 입력 전 `.npz` file geometry adapter 준비
- 이슈 #38: 대표 smoke fixture와 file geometry 결합 smoke
- 이슈 #40: geometry backend 후보 조사와 VGGT 1순위 결정
- 이슈 #42: VGGT geometry adapter skeleton
- 이슈 #44: VGGT 로컬/학교 GPU 실행 환경별 준비 문서
- 이슈 #46 / PR #47: VGGT checkpoint smoke wrapper
- 이슈 #48: VGGT smoke 트러블슈팅 후속 코드/문서 반영
- T17: 실제 노트북 SAM2 mask + VGGT downstream smoke
- T18: 실제 노트북 point cloud outlier filter smoke
- T19: 실제 노트북 5장 multi-view VGGT validation
- 이슈 #56 / T20: 일반 객체용 SAM2 mask cleanup + 3D outlier cleanup preset
- 이슈 #60 / PR A: 방 영상 keyframe extraction + VGGT batch geometry

계속 제외하는 것:

- SAM2 checkpoint/config 파일 커밋
- 실제 VGGT checkpoint 원본 산출물 커밋
- MapAnything adapter 구현
- output 산출물 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 단계별 구현 현황

| 단계 | 상태 | 설명 |
|---|---:|---|
| T1 Capture / frame sampling | 구현됨 | 영상/이미지 입력을 frame record/manifest로 다루는 기본 구조가 있고, 방 영상 keyframe 추출 CLI가 있다. |
| T2 Segmentation adapter | 구현됨 | manual backend와 SAM2 backend가 있다. 실제 SAM2 checkpoint smoke도 통과했다. |
| T3 Geometry adapter | 일부 구현 | mock geometry, `.npz` file geometry loader, VGGT prediction -> `.npz` adapter skeleton, `vggt_geometry` CLI, keyframe manifest 기반 `vggt_geometry_batch` CLI가 있다. 실제 Mac MPS 단일 이미지 VGGT smoke는 성공했고 MapAnything/COLMAP adapter는 아직 없다. |
| T4 Masked back-projection | 구현됨 | mask 영역 픽셀만 3D point로 변환한다. back-projection 전에 mask shape alignment와 largest component / erosion cleanup을 선택적으로 적용할 수 있다. |
| T5 Object point cloud fusion | 구현됨 | point cloud fusion 기본 로직과 radial percentile outlier filter가 있다. 실제 multi-view pose 기반 정합 검증은 아직 약하다. |
| T6 Oriented bbox / object prior | 구현됨 | PCA 기반 oriented bbox와 크기 후보를 만든다. |
| T7 Evaluation | 구현됨 | 기본 metric 계산 구조가 있다. 실제 실측값 기반 검증은 다음 단계에서 강화해야 한다. |
| T8 Visualization | 구현됨 | summary backend와 Rerun backend가 있다. `.rrd` recording 저장도 확인했다. |
| T9 Real-photo validation | 진행 중 | 실제 사진 3장/9개 후보를 문서화했다. 대표 성공/주의/실패 케이스를 분리했다. |

## 검증 결과

- synthetic image smoke
  - SAM2 segmentation CLI → 통과
  - `prior_from_mask` CLI → 통과
  - Rerun `.rrd` recording 저장 → 통과
  - 생성된 recording 파일: `outputs/sam2-to-prior-smoke/prior/sam2-to-prior.rrd`
  - SAM2 confidence: `0.9909150004386902`
  - mask pixels / generated 3D points: `20959`
- 실제 사진 smoke
  - 실제 사용자 사진 3장, 물체 후보 9개 검증
  - 검증 기록: `docs/validation/20260524-real-photo-sam2-object-prior.md`
  - 결과 이미지: `docs/validation/assets/20260524-real-photo-sam2-overlay-contact-sheet.jpg`
  - 성공 대표 후보: 노트북, 영수증, 태블릿+키보드
  - 주의 후보: 투명 컵, 부분 컵, 태블릿 화면
  - 실패 후보: 빨대, 첫 번째 영수증 prompt
- 대표 fixture + file geometry smoke
  - 노트북, 영수증, 태블릿+키보드 synthetic fixture 검증
  - 각 fixture가 `geometry.npz`를 함께 생성
  - `segment_image -> prior_from_mask --geometry-npz` 경로 테스트
  - 결과 이미지: `docs/validation/assets/20260526-representative-fixture-geometry-smoke.jpg`
- 실제 노트북 SAM2 + VGGT mask smoke
  - 같은 실제 노트북 사진과 같은 VGGT `geometry.npz` 사용
  - manual box 대비 SAM2 mask 원본 pixel 26.3% 감소
  - manual box 대비 VGGT geometry effective point count 26.5% 감소
  - 결과 이미지: `docs/validation/assets/20260526-real-laptop-sam2-vggt-mask-comparison.jpg`
- 실제 노트북 point cloud outlier filter smoke
  - 같은 SAM2 mask와 같은 VGGT `geometry.npz` 사용
  - radial percentile filter로 point 5.0% 제거
  - bbox 최대 축 31.2% 감소, bbox volume 후보 38.5% 감소
  - 결과 이미지: `docs/validation/assets/20260526-real-laptop-outlier-filter-3d-comparison.jpg`
- 실제 노트북 5장 multi-view VGGT validation
  - VGGT few-view inference 1회로 view별 `geometry.npz` 생성
  - view별 SAM2 mask와 outlier-filtered prior 생성
  - 같은 노트북인데 largest bbox axis가 `0.334m`부터 `0.508m`까지 흔들림
  - 결론: per-view object prior는 가능하지만 일반적인 clean 3D object extraction으로 보기는 아직 부족
  - 결과 이미지: `docs/validation/assets/20260526-real-laptop-multiview-sam2-overlays.jpg`, `docs/validation/assets/20260526-real-laptop-multiview-3d-priors.jpg`
- 일반 객체용 SAM2 -> 3D cleanup
  - `prior_from_mask`에 `--mask-cleanup largest_component`와 `--mask-erode-pixels` 추가
  - SAM2 mask의 떨어진 조각을 2D에서 제거하고, 3D point cloud의 radial outlier를 다시 제거하는 preset 정리
  - 노트북, 책상, 컵, 가구별 적용 기준과 실패 조건을 runbook에 기록
  - 기존 실제 노트북 5-view 산출물로 smoke를 재실행해 view1/view5의 과도한 bbox가 줄어드는 것을 확인
  - 결과 이미지: `docs/validation/assets/20260526-general-sam2-3d-cleanup-comparison.jpg`
- 방 영상 keyframe + VGGT batch geometry
  - `video_keyframes` CLI로 원본 방 영상에서 reproducible frame manifest와 keyframe 이미지를 생성한다.
  - `vggt_geometry_batch` CLI로 manifest의 keyframe 묶음을 VGGT에 넣고 frame별 `geometry.npz`를 저장한다.
  - 기본 테스트는 synthetic frame source와 injected fake VGGT runner로 고정해 checkpoint 없이 통과한다.

## 실패/주의 케이스 개선 메모

실패/주의 케이스는 제거하지 않고 이후 개선 기준으로 남긴다.

- 실패 케이스: 빨대, 첫 번째 영수증 prompt
- 다음 smoke 후보: 노트북, 영수증, 태블릿+키보드
- 빨대는 일반 object prior 대상에서 제외한다.
  - 필요하면 얇은 물체 전용 후처리로 따로 다룬다.
  - 후보: line extraction, skeletonization, SAM2 video tracking + mask thinning
- 투명 컵은 대표 성공 케이스가 아니라 **투명체 risk set**으로 관리한다.
  - confidence가 높아도 실제 mask 품질이 안정적이지 않을 수 있다.
  - 실제 depth/pose adapter가 붙은 뒤 3D point cloud가 얼마나 흔들리는지 다시 검증한다.
- 첫 번째 영수증 실패는 prompt 개선 후보로 남긴다.
  - 더 타이트한 box
  - negative point 추가
  - prompt 재시도 정책
- 태블릿 화면 단독 분리는 초기 MVP 성공 기준에서 제외한다.
  - 화면 내부 UI와 반사가 mask noise를 만든다.
  - 초기에는 태블릿 전체를 대표 객체로 사용한다.

## 지금 해야 할 다음 작업

우선순위는 다음 순서가 좋다.

1. **Keyframe object segmentation batch**
   - PR A 다음 단계는 keyframe별 노트북/책상/컵/가구 prompt manifest를 만들고, SAM2/manual segmentation을 반복 실행하는 것이다.
2. **Object-aware multi-view fusion**
   - 현재는 keyframe geometry를 만들 수 있지만, view별 prior를 아직 하나로 합치지 않는다.
   - 같은 object id의 view별 point cloud를 하나의 world/object frame으로 합치는 것이 다음 핵심이다.
3. **Open laptop subpart segmentation**
   - 열린 노트북은 화면과 본체가 꺾인 두 평면 구조라 단일 bbox가 불안정하다.
   - `laptop_screen`, `laptop_base`를 분리하면 bbox 안정성이 나아질 가능성이 크다.
4. **실측값 기반 evaluation 강화**
   - 대표 객체 하나를 정하고 실제 width/depth/height를 수동으로 잰다.
   - mock depth 결과와 실제 depth 결과를 분리해서 비교한다.
5. **outlier filter 비교 강화**
   - radial percentile 외에 axis quantile, local density, statistical radius 후보를 비교한다.
   - 얇은 물체처럼 실제로 긴 구조를 과하게 자르지 않는 기준을 정한다.
6. **주의/실패 케이스를 별도 risk set으로 관리**
   - 투명체, 얇은 물체, 화면 반사 물체는 대표 성공 smoke와 분리한다.
   - 개선 작업을 할 때만 별도 PR로 다룬다.

## 아직 하지 않는 것

- 방 전체 3D reconstruction
- Seen2Scene full reproduction
- 3D generative completion 학습
- 대규모 데이터셋 다운로드
- 투명체/얇은 물체 전용 모델 학습
- 자동 prompt 생성 전체 구현
