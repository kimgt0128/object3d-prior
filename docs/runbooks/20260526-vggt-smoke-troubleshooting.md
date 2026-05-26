# VGGT Smoke Troubleshooting Notes

> Scope: T16 / issue #46에서 실제 Mac MPS VGGT smoke 중 밟은 실수와, follow-up issue #48에서 반영한 재발 방지책을 기록한다.

## 요약

실제 노트북 사진 1장으로 VGGT smoke를 실행하면서 다음 문제가 있었다.

```text
Python 3.9 venv
  -> VGGT requires-python >=3.10 실패
Downloads 권한
  -> macOS PermissionError
파일명 변수 불일치
  -> FileNotFoundError
VGGT resized depth와 원본 mask shape 불일치
  -> mask and depth must have the same shape
Rerun을 VGGT venv에 설치
  -> numpy>=2 / numpy<2 dependency 충돌
Rerun spawn PATH
  -> Viewer executable not found
```

## 실수와 조치

| 문제 | 증상 | 원인 | 조치 |
|---|---|---|---|
| Python 3.9 venv | `Package 'vggt' requires a different Python: 3.9.6 not in '>=3.10'` | macOS 기본 `/usr/bin/python3`가 3.9.6 | `/opt/homebrew/bin/python3.11 -m venv .venv-vggt-mps` 사용 |
| Downloads 권한 | `PermissionError: Operation not permitted: /Users/.../Downloads/...jpg` | macOS privacy 권한 | 이미지를 `outputs/.../input/` 아래로 복사해서 사용 |
| 파일명 불일치 | `FileNotFoundError: .../laptop_image1.jpg` | 실제 파일명은 `20260526_185528.jpg`였는데 변수는 `laptop_image1.jpg` | 코드에서 missing image message를 더 구체화 |
| mask/depth shape 불일치 | `ValueError: mask and depth must have the same shape` | VGGT depth는 518x392 resize 결과, manual mask는 원본 4000x3000 | `prior_from_mask`가 mask를 geometry depth shape로 자동 resize |
| Rerun dependency 충돌 | `vggt 0.0.1 has requirement numpy<2, but you have numpy 2.4.6` | 최신 `rerun-sdk`는 `numpy>=2`, VGGT는 `numpy<2` | `.venv-vggt-mps`와 `.venv-rerun` 분리 |
| Rerun viewer PATH | `Failed to find Rerun Viewer executable in PATH` | `.venv-vggt-mps` 활성 상태에서 Rerun spawn 실행 | view_scene에서 Python bin의 `rerun`을 PATH에 자동 추가하고, 실패 시 안내 메시지 개선 |

## 고정된 실행 원칙

VGGT 실행:

```bash
source .venv-vggt-mps/bin/activate
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src python -m object3d.pipeline.vggt_geometry \
  --image-path outputs/real-laptop-vggt-smoke/input/laptop_image1.jpg \
  --output-path outputs/real-laptop-vggt-smoke/image1/geometry.npz \
  --device mps
```

Rerun 보기:

```bash
.venv-rerun/bin/rerun \
  outputs/real-laptop-vggt-smoke/image1/prior/laptop-vggt-smoke.rrd
```

또는 spawn:

```bash
PATH="$PWD/.venv-rerun/bin:$PATH" PYTHONPATH=src .venv-rerun/bin/python -m object3d.visualization.view_scene \
  --manifest outputs/real-laptop-vggt-smoke/image1/prior/scene_manifest.json \
  --backend rerun \
  --spawn
```

## 코드 반영

- `run_vggt_geometry`
  - 입력 이미지가 없으면 `input image not found` 메시지와 확인 방법을 출력한다.
  - macOS 권한 문제로 읽을 수 없으면 workspace 아래로 복사하라는 메시지를 낸다.
  - `geometry.summary.json`에 `geometry_depth_shape`를 기록한다.
- `run_prior_from_mask`
  - mask와 depth shape가 다르면 nearest-neighbor로 mask를 geometry shape에 맞춘다.
  - summary에 `mask_alignment`, `input_mask_shape`, `geometry_depth_shape`, `effective_mask_shape`, `source_mask_npy`, `resized_mask_npy`를 남긴다.
- `view_scene`
  - spawn 시 현재 Python executable의 `bin` 폴더에 있는 `rerun`을 PATH에 자동 추가한다.
  - Viewer executable을 못 찾으면 `.venv-rerun` 실행 예시를 포함한 안내 에러를 낸다.

## 아직 품질 이슈로 남은 것

- 단일 이미지 VGGT point cloud는 화면/책상 경계에서 휘거나 찢어질 수 있다.
- manual box mask는 노트북 윤곽이 아니라 사각형 전체를 포함하므로 point cloud와 bbox가 커질 수 있다.
- 다음 품질 개선은 SAM2 mask, outlier removal, #1+#3+#4 multi-view smoke 순서로 진행한다.
