# General SAM2 to Clean 3D Object Prior Runbook

> Scope: #56 / T20. 노트북에 국한하지 않고, 책상, 컵, 가구 같은 일반 물체에서 SAM2 mask를 3D point cloud와 bbox로 올릴 때 점이 튀는 문제를 줄이는 기본 절차를 정리한다.

## 결론

SAM2의 객체 탐지는 2D mask를 만든다. 이 mask에 배경, 테이블, 그림자, 반사 영역이 조금이라도 섞이면 해당 픽셀도 depth와 결합되어 3D 점이 된다. 그래서 깨끗한 3D 시각화를 위해서는 아래 순서가 필요하다.

```text
SAM2 mask
  -> mask cleanup
  -> geometry depth shape 정렬
  -> masked back-projection
  -> point cloud outlier filtering
  -> bbox / Rerun 시각화
```

쉽게 말하면, **2D에서 한 번 청소하고 3D에서 한 번 더 청소한다.**

## 추천 기본 옵션

일반적인 책상 위 물체, 노트북, 작은 가구처럼 표면이 어느 정도 덩어리로 잡히는 물체는 다음 조합부터 사용한다.

```bash
PYTHONPATH=src .venv/bin/python -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/example/segmentation/summary.json \
  --output-dir outputs/example/prior-clean \
  --geometry-npz outputs/example/geometry.npz \
  --mask-cleanup largest_component \
  --mask-erode-pixels 1 \
  --outlier-filter radial_percentile \
  --outlier-keep-ratio 0.95
```

옵션 의미:

- `--mask-cleanup largest_component`: mask 안에서 가장 큰 연결 덩어리만 남긴다. 떨어져 있는 작은 배경 조각, 잘못 찍힌 섬 점을 제거한다.
- `--mask-erode-pixels 1`: mask 경계를 한 픽셀 정도 안쪽으로 깎는다. 테이블/배경이 경계에 얇게 붙어 들어온 경우를 줄인다.
- `--outlier-filter radial_percentile`: 3D로 올라간 뒤 중심에서 너무 멀리 튄 꼬리 점을 제거한다.
- `--outlier-keep-ratio 0.95`: 3D 점의 약 95%를 유지하고 바깥쪽 5% tail을 제거한다.

## 물체별 기준

| 대상 | 추천 | 주의 |
|---|---|---|
| 노트북 | `largest_component`, `erode 1`, `radial_percentile 0.95` | 열린 노트북은 화면과 본체를 나누는 subpart segmentation이 더 좋다. |
| 책상/가구 | `largest_component`, `erode 1-2`, `radial_percentile 0.95` | 큰 평면은 bbox가 물체 전체보다 visible surface에 맞춰질 수 있다. |
| 컵 | `largest_component`, `erode 0-1` | 투명/반사 컵은 depth가 불안정하므로 risk set으로 관리한다. |
| 얇은 물체 | `erode 0` | 빨대, 선, 케이블은 erosion이 실제 물체를 없앨 수 있다. |
| 화면/반사 물체 | `largest_component`, negative prompt 강화 | SAM2 confidence가 높아도 반사 때문에 3D depth가 흔들릴 수 있다. |

## 아직 해결되지 않는 경우

`largest_component`는 떨어진 조각에는 강하지만, 테이블이 물체 mask와 하나로 붙어서 들어오면 완전히 제거하지 못한다. 이 경우는 다음 중 하나가 필요하다.

- SAM2 prompt에 negative point를 추가한다.
- object와 table의 depth discontinuity를 이용해 mask 내부를 다시 자른다.
- 여러 view의 point cloud를 합친 뒤 density 기반 filter를 적용한다.
- 노트북처럼 꺾인 구조는 `screen`, `base`처럼 subpart로 분리한다.

## 좋은 입력 사진 기준

- 물체 전체가 화면 안에 들어와야 한다.
- 물체와 배경 색이 너무 비슷하지 않은 각도가 좋다.
- 투명 컵, 반사 화면, 검은 물체와 검은 배경 조합은 실패 분석용으로 따로 둔다.
- 다각도 검증은 3-5장부터 시작하되, 처음에는 가장 선명한 1장으로 smoke를 통과시키는 것이 좋다.

## 판단 기준

성공으로 볼 수 있는 상태:

- mask overlay에서 배경 조각이 크게 보이지 않는다.
- `mask_pixels_after_cleanup`이 `mask_pixels_before_cleanup`보다 줄어도 핵심 물체가 사라지지 않는다.
- `filtered_point_count`가 `input_point_count`보다 조금 줄고, bbox가 과도하게 길어지지 않는다.
- Rerun 또는 정적 preview에서 점들이 하나의 물체 표면 주변에 모인다.

실패로 기록해야 하는 상태:

- cleanup 뒤 mask가 비거나 핵심 물체가 깎인다.
- bbox가 물체보다 테이블/배경 방향으로 길게 끌린다.
- view마다 같은 물체의 `dimensions_m`이 크게 흔들린다.
- 투명체/반사체에서 depth가 구멍 나거나 튄다.
