# Geometry Backend Candidate Selection

> Scope: T13 / issue #40. 실제 model adapter를 구현하기 전에 VGGT, MapAnything, COLMAP 중 다음 PR에서 먼저 붙일 backend를 고른다.

## 결론

다음 구현 1순위는 **VGGT adapter skeleton**으로 잡는다.

쉽게 말하면, 지금 프로젝트는 이미 `geometry.npz`라는 표준 입력 그릇을 만들었다. 이제 필요한 것은 실제 depth/pose 모델 하나의 출력을 그 그릇에 담는 일이다. VGGT는 한 장 또는 여러 장의 이미지를 넣으면 camera intrinsics/extrinsics, depth map, point map을 바로 예측하는 구조라서 현재 `GeometryRecord(depth_m, intrinsics, camera_to_world)` 계약에 가장 빠르게 연결할 수 있다.

후보 순위:

1. **VGGT**: 다음 PR에서 adapter skeleton 구현
2. **MapAnything**: metric reconstruction 후보로 후속 PR에서 검토/구현
3. **COLMAP**: multi-view baseline과 sanity check 용도로 뒤에 구현

## 현재 프로젝트가 필요한 출력

우리 downstream은 raw model output을 직접 보지 않는다. 모든 실제 geometry backend는 아래 `.npz` 계약으로 정규화해야 한다.

```text
depth_m          # (H, W), meter 단위 depth map
intrinsics       # (3, 3), pinhole camera matrix
camera_to_world  # (4, 4), camera -> world transform
```

이 파일을 만든 뒤에는 기존 CLI가 그대로 이어진다.

```bash
PYTHONPATH=src python3 -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/.../summary.json \
  --output-dir outputs/.../prior \
  --geometry-npz outputs/.../geometry.npz
```

## 후보 비교

| 후보 | 쉽게 말하면 | 우리 계약과의 맞음 | 장점 | 리스크 | 판단 |
|---|---|---:|---|---|---|
| VGGT | 사진을 보고 depth와 camera를 한 번에 추정하는 feed-forward 모델 | 높음 | depth map, camera intrinsics/extrinsics, point map이 바로 나옴. 한 장/소수 이미지 smoke에 좋음. | checkpoint/license 선택과 GPU/메모리 확인 필요. 예측 depth의 metric scale은 실제 검증 필요. | 1순위 |
| MapAnything | metric 3D reconstruction을 목표로 한 통합 framework | 높음 | metric output 지향. 자체 모델과 외부 모델을 unified interface로 감쌈. `depth_z`, world/camera points, camera pose 계열 출력이 있음. | 환경이 더 무거움. Python 3.12/extra install, model license 선택 필요. | 2순위 |
| COLMAP | 여러 사진의 feature matching으로 camera pose와 3D 구조를 복원하는 전통 도구 | 중간 | 검증된 baseline. CLI와 sparse/dense reconstruction pipeline이 명확함. | 단일 사진에는 부적합. 충분한 multi-view 입력과 feature가 필요. dense depth까지 가면 절차가 길고 무거움. | baseline |

## VGGT

공식 README 기준 VGGT는 one/few/hundreds views에서 camera extrinsics, intrinsics, point maps, depth maps, 3D point tracks를 예측한다.

프로젝트에 맞는 이유:

- `intrinsics`와 camera extrinsics가 adapter 입력으로 바로 쓸 수 있는 형태에 가깝다.
- `depth_map`을 `depth_m`로 정규화할 수 있다.
- `extrinsic`의 좌표계만 확인하면 `camera_to_world`로 변환하는 adapter skeleton을 만들 수 있다.
- 한 장 또는 소수 대표 사진 smoke를 만들기 쉽다.
- `demo_colmap.py`도 있어 나중에 COLMAP format export와 연결할 여지가 있다.

주의할 점:

- 모델 checkpoint license가 나뉜다. 공식 README는 commercial-friendly checkpoint와 original checkpoint license 차이를 명시한다.
- GPU/메모리 조건을 확인해야 한다. 공식 업데이트에 메모리 최적화 언급이 있지만, 로컬 smoke는 작은 이미지부터 시작한다.
- 첫 adapter PR에서는 실제 checkpoint 다운로드를 강제하지 않는다. optional dependency와 lazy import 경로로 둔다.

다음 PR에서 할 일:

- `object3d.adapters.geometry.vggt` skeleton 추가
- VGGT raw prediction을 우리 `.npz` 계약으로 저장하는 함수 설계
- 실제 VGGT import가 없어도 기본 test suite가 깨지지 않도록 optional dependency error 추가
- synthetic prediction dict 또는 fake runner로 adapter 변환 테스트 작성

참고:

- [facebookresearch/vggt](https://github.com/facebookresearch/vggt)
- [VGGT arXiv](https://arxiv.org/abs/2503.11651)

## MapAnything

공식 README 기준 MapAnything은 universal metric 3D reconstruction framework이며, images/calibration/poses/depth 같은 다양한 입력으로 metric scene geometry를 예측한다. 자체 모델뿐 아니라 VGGT, DUSt3R, MASt3R, Pi3-X 등 외부 모델도 unified interface로 감쌀 수 있다.

프로젝트에 맞는 이유:

- metric reconstruction 지향이라 실제 크기 추정 목표와 잘 맞는다.
- `depth_z`, `pts3d`, `pts3d_cam`, camera translation/quaternion 계열 출력이 있어 `depth_m`과 `camera_to_world` 변환 후보가 명확하다.
- 나중에 여러 backend 비교 framework로 확장하기 좋다.

주의할 점:

- 설치가 더 무겁다. 공식 README는 conda Python 3.12 환경과 optional `[all]` install을 안내한다.
- model license가 나뉜다. research/academic용 default와 Apache 2.0 friendly model을 구분해야 한다.
- 첫 MVP adapter로 바로 붙이면 범위가 커질 수 있다.

판단:

- VGGT skeleton 뒤에 metric smoke용으로 붙이는 것이 좋다.
- 실제 치수 평가 PR 전에는 MapAnything을 다시 후보로 올린다.

참고:

- [facebookresearch/map-anything](https://github.com/facebookresearch/map-anything)
- [MapAnything arXiv](https://arxiv.org/abs/2509.13414)

## COLMAP

COLMAP은 feature extraction, matching, mapper, image undistorter, patch match stereo, stereo fusion 같은 단계로 sparse/dense reconstruction을 수행한다.

프로젝트에 맞는 이유:

- multi-view camera pose sanity check에 좋다.
- neural backend 결과가 이상할 때 비교할 전통 baseline으로 유용하다.
- CLI가 명확해 자동화할 수 있다.

주의할 점:

- 단일 이미지 MVP에는 맞지 않는다.
- texture가 약하거나 겹침이 부족한 스마트폰 영상에서는 실패할 수 있다.
- dense depth까지 가려면 절차와 실행 시간이 길다.

판단:

- 지금 당장 첫 실제 adapter로 붙이기보다, multi-view capture가 안정된 뒤 baseline으로 붙인다.

참고:

- [COLMAP command-line interface](https://colmap.github.io/cli.html)
- [COLMAP installation](https://colmap.readthedocs.io/en/latest/install.html)

## 다음 PR 제안

**T14: VGGT adapter skeleton** — 구현됨

목표:

- 실제 모델 실행 전체가 아니라, VGGT output을 `geometry.npz`로 바꾸는 adapter 모양을 먼저 만든다.
- optional dependency를 유지한다.
- fake VGGT prediction으로 `depth_m`, `intrinsics`, `camera_to_world` 변환 테스트를 통과시킨다.

완료 기준:

- `src/object3d/adapters/geometry/vggt.py` 추가
- `save_vggt_geometry_npz(...)` 또는 그에 준하는 변환 함수 추가
- VGGT raw camera/depth output -> `.npz` 저장 테스트 추가
- README/PLAN에 실제 checkpoint smoke는 다음 T로 분리한다고 명시

좌표계 주의:

- VGGT 공식 README는 extrinsic을 OpenCV convention의 camera-from-world로 설명한다.
- 내부 `GeometryRecord` 계약은 `camera_to_world`만 받는다.
- 따라서 VGGT adapter는 extrinsic을 역행렬로 변환해 `camera_to_world`에 저장한다.

아직 하지 않는 것:

- checkpoint 다운로드
- GPU inference 자동화
- 실제 사진 smoke
- MapAnything/COLMAP 구현
