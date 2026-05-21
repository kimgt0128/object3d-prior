# 아키텍처와 모듈 경계 규칙

이 파일은 실제 source layout과 모듈 책임이 커져도 흐트러지지 않도록 기준을 정한다.

## 최상위 구조

```text
configs/
data/
src/object3d/
apps/
scripts/
tests/
docs/
.claude/
```

## 모듈 책임

- `capture/`: frame sampling, metadata, manual measurement
- `adapters/segmentation/`: SAM/SAM2/Grounded SAM output 정규화
- `adapters/geometry/`: MapAnything/VGGT/COLMAP output 정규화
- `geometry/`: back-projection, scale alignment, pose sanity check
- `reconstruction/`: object point fusion, outlier filtering
- `priors/`: bbox, dimension, orientation, placement constraint
- `evaluation/`: 실측값 비교, ablation, threshold 기록
- `visualization/`: mask overlay, point cloud, bbox, demo evidence
- `pipeline/`: 단계 연결과 config-driven 실행

## 경계 규칙

- 외부 모델 raw output format을 프로젝트 전체로 퍼뜨리지 않는다.
- adapter는 raw output과 normalized contract를 분리한다.
- demo UI가 core geometry logic을 직접 소유하지 않는다.
- geometry contract가 바뀌면 reconstruction과 priors를 함께 검토한다.
- data path convention이 바뀌면 experiment log와 visualization도 함께 갱신한다.

## 먼저 만들지 말 것

- 코드가 없는데 거대한 package tree부터 만들지 않는다.
- full-room reconstruction 전용 module부터 만들지 않는다.
- 학습 코드가 no-training MVP보다 먼저 나오지 않는다.
- source folder 안에 generated data를 숨기지 않는다.

## 멈출 조건

- 새 폴더 owner가 불명확하다.
- 같은 역할이 두 module에 중복된다.
- routing 문서와 실제 module boundary가 다르다.
- generated data와 source code가 섞인다.
