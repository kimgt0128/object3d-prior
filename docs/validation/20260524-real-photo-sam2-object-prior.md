# 2026-05-24 실제 사진 SAM2 object prior 검증

## 목적

사용자가 직접 촬영한 카페 테이블 사진 3장으로 `segment_image -> prior_from_mask -> view_scene` 흐름을 다시 확인했다.

이번 검증은 실제 depth 모델이 아니라 `--depth-m 2.0` mock depth를 사용한다. 따라서 아래의 `dimensions_m` 값은 실제 물체 치수가 아니다. 이번 검증의 목적은 **실제 사진에서 SAM2 mask가 만들어지고, 그 mask가 3D point cloud, oriented bbox, Rerun recording까지 이어지는지 확인**하는 것이다.

## 입력 이미지

- `20260524_162710.jpg`
- `20260524_162734.jpg`
- `20260524_162727.jpg`

원본 사진은 로컬에서만 사용했고 git에는 포함하지 않는다. 파일 메타데이터 기준으로는 모두 `4000 x 3000`급 RGB 이미지이며, 실제 SAM2 처리 결과의 `mask_shape`은 이미지 방향과 decoder 처리 방식에 따라 케이스별로 다르게 기록될 수 있다.

## 실행 흐름

1. 물체별 prompt JSON을 작성했다.
2. `segment_image --backend sam2`로 mask와 overlay를 생성했다.
3. `prior_from_mask --depth-m 2.0`으로 mask pixel을 mock 3D point cloud로 변환했다.
4. PCA 기반 oriented bbox를 생성했다.
5. `view_scene --backend rerun --save-rrd`로 Rerun recording 파일을 저장했다.

산출물은 `outputs/real-photo-validation-20260524/` 아래에 저장했다. `outputs/`는 git 추적 대상이 아니므로 PR에는 이 문서만 포함한다.

## 결과 요약

| 케이스 | 대상 | 판단 | SAM2 confidence | mask pixels | point count | Rerun | 메모 |
|---|---|---:|---:|---:|---:|---|---|
| `162710_cup` | 큰 투명 컵 | 주의 | 0.708 | 1,309,921 | 1,309,921 | 7.0MB | 컵 몸체는 잡았지만 투명 재질과 탁자 일부가 섞였다. |
| `162710_straw` | 빨대 | 실패 | 0.683 | 936,029 | 936,029 | 5.0MB | 얇은 빨대만 분리하지 못하고 컵/탁자 영역이 크게 섞였다. |
| `162710_receipt` | 구겨진 영수증 | 실패 | 0.857 | 185,108 | 185,108 | 1.1MB | 실제 영수증보다 컵 상단/주변부를 잡았다. |
| `162734_laptop` | 노트북 | 성공 | 0.772 | 3,527,264 | 3,527,264 | 18.8MB | 화면, 키보드, 본체를 대부분 포함했다. 큰 객체 대표 샘플로 적합하다. |
| `162734_receipt` | 영수증 | 성공 | 0.971 | 115,567 | 115,567 | 0.6MB | 작은 종이 객체를 깔끔하게 분리했다. |
| `162734_notebook` | 포장지/작은 평면 물체 | 성공 | 0.895 | 301,027 | 301,027 | 1.5MB | 처음 라벨은 notebook이었지만 실제로는 하단 포장지를 잘 잡았다. |
| `162734_cup_partial` | 부분 컵 | 주의 | 0.965 | 437,365 | 437,365 | 2.2MB | 오른쪽에 잘린 투명 컵도 꽤 잘 잡지만 crop 때문에 bbox 의미가 제한된다. |
| `162727_tablet_full` | 태블릿+키보드 | 성공 | 0.954 | 5,754,868 | 5,754,868 | 30.0MB | 전체 기기 윤곽을 가장 안정적으로 분리했다. |
| `162727_screen` | 태블릿 화면 | 주의 | 0.842 | 2,016,846 | 2,016,846 | 10.5MB | 화면 영역은 잡지만 내부 UI/반사 때문에 mask가 거칠고 노이즈가 있다. |

## 해석

이번 사진들은 이전 사진보다 검증 가치가 높다. 특히 `162734_laptop`, `162734_receipt`, `162727_tablet_full`은 실제 사진 기반 smoke test 대표 케이스로 쓰기 좋다.

투명 컵은 confidence가 높게 나와도 실제 mask 품질이 항상 좋은 것은 아니었다. 투명 재질은 배경이 비쳐 보이고 경계가 흐려서, SAM2가 컵 표면과 뒤쪽 탁자/그림자를 섞어 잡을 수 있다.

빨대처럼 매우 얇은 물체는 현재 prompt 방식으로는 안정적인 object prior 대상이 아니다. 빨대 하나만 잡으려면 더 촘촘한 point prompt, video tracking, 또는 후처리 기반 skeleton/line extraction이 필요하다.

태블릿 전체처럼 경계가 크고 명확한 물체는 가장 안정적이었다. 반면 태블릿 화면만 따로 잡으면 내부 UI, 반사, 어두운 화면 영역 때문에 mask가 거칠어진다.

## 주의/실패 케이스 처리 방침

주의/실패 케이스는 버리지 않는다. 이 프로젝트의 목적은 "잘 되는 사진만 보여주는 데모"가 아니라, 어떤 객체가 3D object prior 후보로 적합한지 판단하는 것이다. 따라서 실패 케이스는 후속 개선의 기준선으로 남긴다.

| 유형 | 현재 판단 | 다음 처리 |
|---|---|---|
| 투명 컵 | mask는 잡히지만 배경/탁자와 섞인다. | 성공 케이스가 아니라 "투명체 주의 케이스"로 분리한다. 나중에 depth 모델을 붙인 뒤 실제 3D 점군이 얼마나 흔들리는지 다시 본다. |
| 빨대 | 얇은 선형 물체라 SAM2 mask가 주변까지 크게 먹는다. | 일반 object prior 대상에서 제외한다. 필요하면 line/skeleton extraction 같은 얇은 물체 전용 후처리로 따로 다룬다. |
| 구겨진 영수증 실패 케이스 | box와 point prompt가 컵 주변부로 끌려갔다. | 더 타이트한 box, negative point 추가, 또는 prompt 재시도 정책이 필요하다. |
| 태블릿 화면만 분리 | 화면 내부 UI와 반사가 mask 노이즈를 만든다. | 초기 MVP에서는 화면만 따로 측정하지 말고 태블릿 전체를 대표 객체로 사용한다. |

초기 regression smoke에는 `162734_laptop`, `162734_receipt`, `162727_tablet_full`만 성공 대표 케이스로 쓰는 것이 좋다. `주의` 케이스는 별도 risk set으로 보관하고, `실패` 케이스는 prompt/postprocess 개선 작업의 입력으로 둔다.

## 코드리뷰 관점

이번 변경은 실행 코드 변경이 아니라 검증 문서 추가다. 리뷰에서는 다음을 확인하면 된다.

- 실제 depth가 아니라 mock depth `2.0m`를 사용했다는 제한이 명확히 적혀 있는가?
- 성공 케이스만 적지 않고 주의/실패 케이스도 함께 기록했는가?
- `outputs/`, checkpoint, 원본 사진 같은 큰 산출물이 git에 들어가지 않았는가?
- 다음 PR에서 어떤 케이스를 대표 smoke로 삼을지 판단할 수 있는가?

## PR 설명에 넣을 요약 초안

실제 사용자 사진 3장을 대상으로 SAM2 segmentation 결과를 3D prior 파이프라인까지 연결 검증했다.

- `segment_image --backend sam2`로 9개 물체 후보를 테스트했다.
- 모든 케이스에서 `mask.npy`, `overlay.png`, `summary.json`을 생성했다.
- 모든 케이스를 `prior_from_mask --depth-m 2.0`에 연결해 point cloud와 oriented bbox를 생성했다.
- 모든 케이스를 Rerun `.rrd` recording으로 저장했다.
- 대표 성공 케이스는 노트북, 영수증, 태블릿+키보드다.
- 투명 컵, 빨대, 화면 일부처럼 경계가 애매하거나 얇은 물체는 실패/주의 케이스로 기록했다.

중요한 제한: 현재 3D 변환은 실제 depth가 아니라 mock depth `2.0m`를 사용한다. 따라서 이번 PR의 의미는 실제 치수 정확도 검증이 아니라, 실제 SAM2 mask가 object prior 파이프라인에 정상 연결되는지 확인한 것이다.

## 다음 작업 제안

1. 대표 성공 케이스 3개만 남겨 regression smoke fixture를 만든다.
2. 실패 케이스는 prompt 개선 또는 후처리 후보로 분리한다.
3. 이후 MapAnything/VGGT depth adapter가 붙으면 같은 사진으로 실제 scale 검증을 다시 수행한다.
