# 객체 인식 기반 3D 공간 도우미 구현 전략

> 에이전트 작업자용 기준 문서: 이 파일은 단계 인덱스만 담는다. 세부 구현 단계가 필요할 때만 [implementation-phases.md](../plans/ref/implementation-phases.md)를 연다.

**목표:** SAM 계열 모델의 2D mask를 3D object prior로 승격해, 객체 추적, 크기 측정, 배치 가능성 판단까지 수행하는 실용적인 컴퓨터 비전 파이프라인을 만든다.

**구조:** 외부 pretrained 모델은 segmentation, tracking, depth, pose를 제공한다. 이 프로젝트가 직접 책임지는 부분은 정제, 정렬, fusion, 측정, 평가, 시각화다.

**기술 스택:** Python, OpenCV, NumPy, SciPy, Open3D, Rerun, PyTorch, SAM 계열 모델, MapAnything 또는 VGGT, 선택적으로 COLMAP.

---

## 먼저 하지 말 것

- 방 전체 dense reconstruction부터 시작하지 않는다.
- Seen2Scene 전체 학습 재현을 첫 목표로 잡지 않는다.
- 단일 객체 MVP가 동작하기 전에 거대한 3D dataset을 받지 않는다.
- 파일 입출력 계약이 안정되기 전에 모든 모델을 한 번에 붙이지 않는다.
- mask overlay를 눈으로 확인하기 전에 3D 측정으로 넘어가지 않는다.

## 단계 인덱스

| 단계 | 담당 | 목표 | 다음 단계로 넘어가기 전 조건 |
|---|---|---|---|
| 0 | Research + Data Capture | 첫 model stack, 대상 객체, 촬영 규칙 선택 | segmentation 경로 1개와 geometry 경로 1개가 정해짐 |
| 1 | Segmentation | 한 객체를 프레임 전체에서 추적 | mask가 안정적이고 overlay가 확인됨 |
| 2 | Geometry + Reconstruction | mask 픽셀을 3D object point로 역투영 | 1프레임/2프레임 geometry 검사가 통과됨 |
| 3 | Object Prior | 치수, 방향, confidence 추정 | 축 convention과 단위가 문서화됨 |
| 4 | Evaluation | 수동 실측값과 비교 | 절대 오차와 상대 오차가 기록됨 |
| 5 | Visualization + Integration | 사용자에게 보이는 측정/배치 demo 제작 | confidence와 실패 이유가 화면에 드러남 |

## 학습과 튜닝 순서

이 프로젝트는 처음부터 dataset fine-tuning을 목표로 하지 않는다. 먼저 pretrained model 조합과 geometry pipeline이 end-to-end로 동작해야 한다.

권장 순서는 다음과 같다.

1. **No-training MVP**: SAM/SAM2, MapAnything/VGGT/COLMAP output을 조합해 단일 객체 mask, depth/pose, point cloud, bbox, 치수 평가까지 연결한다.
2. **파라미터 튜닝**: mask confidence threshold, frame filtering, outlier removal, bbox fitting, scale alignment를 조정한다.
3. **데이터셋 기반 조정 검토**: 반복 실패 유형이 쌓인 뒤 어떤 병목을 데이터로 개선할지 정한다.
4. **가벼운 fine-tuning 또는 학습**: 필요할 때만 mask refinement, depth correction, confidence calibration, object dimension regression 같은 좁은 병목 하나를 선택한다.

대규모 3D scene completion 학습이나 Seen2Scene식 full training은 MVP 이후 연구 확장으로만 다룬다.

## 상세 설명 분리 규칙

이 파일은 phase index 역할만 한다. 특정 단계가 길어지거나 구현자가 배경지식 없이 따라가기 어렵다면 본문에 모두 넣지 않고 `.claude/plans/ref/` 아래에 상세 설명 문서를 만든다.

상세 설명 문서가 필요한 경우:

- 단계별 작업이 5개 이상의 하위 task로 나뉜다.
- 모델 선택, 데이터 schema, coordinate convention처럼 실수하면 downstream이 깨지는 결정이다.
- 테스트 명령, expected output, 실패 기준을 구체적으로 적어야 한다.
- 사용자 결정이 필요한 trade-off가 있다.
- Superpowers 계획 형식처럼 checkbox 기반 실행 계획이 필요하다.

상세 설명 문서는 [plans/ref/README.md](ref/README.md)의 규칙을 따른다.

## 권장 커밋 단위

커밋 메시지는 실제 작업 시 [rules/ref/commit-pr-format.md](../rules/ref/commit-pr-format.md)의 한글 규칙을 따른다. 아래는 기능을 나누는 기준이다.

```text
docs(project): 초기 model stack과 촬영 제약 정의
feat(segmentation): prompt 기반 객체 추적 추가
feat(geometry): mask 픽셀을 world-space object point로 변환
feat(priors): 객체 치수와 방향 추정
feat(evaluation): 실측값 기준 객체 측정 오차 비교
feat(pipeline): 객체 측정 및 배치 가능성 리포트 생성
```

## 필수 리뷰 게이트

- Segmentation 변경: mask overlay 리뷰가 필요하다.
- Geometry 변경: 1프레임 point cloud 리뷰가 필요하다.
- Reconstruction 변경: fused object cloud 리뷰가 필요하다.
- Object prior 변경: 수동 실측값 비교가 필요하다.
- Demo 변경: 시각 검증이 필요하다.

## 세부 참고 문서

현재 명령이 단계별 구현 절차를 필요로 할 때만 [implementation-phases.md](../plans/ref/implementation-phases.md)를 연다.
