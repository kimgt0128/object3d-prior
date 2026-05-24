# Current Implementation Plan

> **운영 기준:** 큰 기능은 T 단위 Issue/Branch/PR로 묶고, 내부 커밋은 세부 작업 단위로 쌓는다. PR 설명은 어려운 용어를 풀어서 쓴다.

## 현재 상태

- capture, segmentation adapter, mock geometry, masked back-projection, point cloud fusion, PCA oriented bbox, evaluation이 연결되어 있다.
- `segment_image` CLI는 `manual`과 `sam2` backend를 선택할 수 있다.
- `prior_from_mask` CLI는 segmentation 결과를 3D point cloud, bbox, scene manifest로 바꿀 수 있다.
- scene manifest는 summary backend와 Rerun lazy backend로 열 수 있다.
- Rerun backend는 `.rrd` recording 파일로 3D 장면을 저장할 수 있다.

## 이번 작업: Issue #30 T10 실제 SAM2 mask를 3D prior 파이프라인에 연결 검증

목표는 실제 SAM2가 만든 mask 결과를 3D prior 단계까지 넣어보는 것이다.
쉽게 말하면 "SAM2가 이미지에서 객체를 잘라낸 결과"를 "3D 점구름, bbox, 다시 열어볼 수 있는 3D 장면 파일"까지 이어본다.

## 작업 범위

수정/생성:

- `src/README.md`
- `docs/PLAN.md`

수정하지 않음:

- SAM2 checkpoint/config 파일 커밋
- 실제 depth 모델 연결
- MapAnything/VGGT adapter 구현
- output 산출물 커밋
- `project/`, `cv_tutorial/`, `reference/`

## 실행한 흐름

1. synthetic image와 box prompt를 준비한다.
2. 실제 `sam2.1_hiera_tiny.pt` checkpoint로 `segment_image --backend sam2`를 실행한다.
3. SAM2가 만든 `summary.json`을 `prior_from_mask`에 넣는다.
4. mock depth 값 `2.0m`를 사용해 3D point cloud와 oriented bbox를 만든다.
5. scene manifest를 Rerun backend로 열고 `.rrd` recording 파일을 저장한다.

## 검증 결과

- SAM2 segmentation CLI smoke → 통과
- `prior_from_mask` CLI smoke → 통과
- Rerun `.rrd` recording 저장 → 통과
- 생성된 recording 파일: `outputs/sam2-to-prior-smoke/prior/sam2-to-prior.rrd`
- SAM2 confidence: `0.9909150004386902`
- mask pixels: `20959`
- generated 3D points: `20959`
- recording file size: 약 `126KB`

## 다음 후보

1. 실제 사용자 이미지 1장으로 같은 흐름 반복
2. MapAnything/VGGT depth/pose adapter contract 추가
3. Rerun GUI spawn 화면 검증
