# src

이 폴더는 객체 인식 기반 3D 공간 보조 프로젝트의 실제 구현 코드를 담는다.

초기 목표는 방 전체를 한 번에 복원하는 것이 아니라, 스마트폰 영상 속 단일 객체를 SAM 계열 모델로 추적하고 depth/pose와 결합해 3D object prior를 만드는 것이다.

## 예상 모듈

- `capture/`: frame sampling, 촬영 metadata, 실측값 정리
- `adapters/`: SAM, MapAnything, VGGT, COLMAP 출력 정규화
- `geometry/`: back-projection, scale alignment, pose sanity check
- `reconstruction/`: masked point cloud fusion, outlier filtering
- `priors/`: bounding box, dimension, orientation, placement 판단
- `evaluation/`: 실측값 비교, metric, ablation 기록
- `visualization/`: mask overlay, point cloud, 3D bounding box 시각화
- `pipeline/`: end-to-end 실행 흐름 연결

자세한 구조 기준은 `project/references/future-code-layout.md`를 따른다.
