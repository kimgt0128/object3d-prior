# src

이 폴더는 객체 인식 기반 3D 공간 보조 프로젝트의 실제 구현 코드를 담는다.

초기 목표는 방 전체를 한 번에 복원하는 것이 아니라, 스마트폰 영상 속 단일 객체를 SAM 계열 모델로 추적하고 depth/pose와 결합해 3D object prior를 만드는 것이다.

## 구현된 MVP 모듈

- `object3d.capture`: frame sampling, 촬영 metadata, manifest 생성
- `object3d.contracts`: mask, geometry, point cloud, object prior 데이터 계약
- `object3d.adapters.segmentation.mock`: SAM/SAM2 연동 전 mock mask adapter
- `object3d.adapters.geometry.mock`: 실 geometry 모델 연동 전 mock depth/pose adapter
- `object3d.geometry`: masked back-projection
- `object3d.reconstruction`: object point cloud fusion
- `object3d.priors`: bbox 기반 object prior fitting
- `object3d.evaluation`: 실측값 대비 dimension error 계산
- `object3d.visualization`: point cloud PLY export
- `object3d.pipeline`: mock 기반 end-to-end 실행 흐름

첫 MVP는 실제 SAM/SAM2와 MapAnything/VGGT를 바로 붙이지 않는다.
먼저 contract와 downstream geometry pipeline을 검증한 뒤 실제 adapter를 추가한다.

## Mock MVP 실행

아직 패키지 설치 설정을 두지 않았으므로 로컬 실행은 `PYTHONPATH=src`를 붙인다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline --output-dir outputs/mock-mvp
```

실행하면 다음 산출물이 생성된다.

- `outputs/mock-mvp/summary.json`: 객체 prior, 치수 오차, PLY 경로 요약
- `outputs/mock-mvp/object_001_cloud.ply`: mock 객체 point cloud
