# VGGT Runtime Environment Runbook

> Scope: T15 / issue #44. 실제 VGGT checkpoint smoke를 실행하기 전에 로컬 Mac과 학교 NVIDIA GPU 장비의 준비 절차를 분리한다.

## 결론

다음 실제 VGGT smoke는 **학교 NVIDIA RTX 30/40 series CUDA 장비**를 기본 경로로 잡는 것이 좋다. 로컬 MacBook Pro M5는 Apple Silicon/MPS smoke로 쓸 수 있지만, 첫 성공 기준은 1장짜리 입력으로 작게 잡는다.

쉽게 말하면:

- 로컬 Mac: "설치가 되는지, 1장짜리 작은 smoke가 도는지" 확인하는 안전한 작업대
- 학교 GPU: "실제 VGGT depth/pose를 뽑고 `geometry.npz`로 저장하는" 기본 실행 환경

H100 같은 데이터센터 GPU가 없어도 바로 양자화부터 할 필요는 없다. 먼저 이미지 수와 해상도를 줄이고, `torch.no_grad()`/mixed precision을 쓰는 smoke로 시작한다. 양자화나 chunking은 1-4장 smoke도 메모리에 안 맞을 때 검토한다.

## Smoke 규모 기준

| 환경 | 기본 smoke | 늘려볼 수 있는 범위 | 판단 |
|---|---:|---:|---|
| MacBook Pro M5 / Apple Silicon MPS | 1장 | 2장 | dependency와 adapter 연결 확인용. 장시간/다중 이미지 실험은 기본값으로 두지 않는다. |
| RTX 30/40 8GB급 | 1장 | 2장 | 설치 검증과 단일 객체 smoke에 적합하다. |
| RTX 3060 12GB / RTX 4070 12GB급 | 1장 | 2-4장 | 현재 MVP에 가장 현실적인 학교 장비 기준이다. |
| RTX 4070 Ti SUPER 16GB / RTX 4080 16GB 이상 | 1-4장 | 8-10장 | multi-view smoke까지 확장 후보. |
| RTX 4090 24GB급 | 4장 | 10장 이상 | 실제 scale 검증 전 후보를 넓히기 좋다. |

여기서 "GTX 4070"이라고 부르는 장비는 보통 **RTX 4070**을 의미한다. NVIDIA 40 series는 RTX 라인이다.

## 로컬 MacBook Pro M5

### 목적

로컬은 CUDA가 아니라 PyTorch MPS backend를 쓴다. VGGT 공식 quick start는 CUDA가 있으면 CUDA를 쓰고 없으면 CPU로 가는 흐름을 보여주므로, MPS는 우리가 로컬 개발 편의를 위해 따로 확인해야 하는 경로다. 그래서 목표는 "개발 중 빠르게 import/setup을 확인하고, 대표 fixture 1장으로 아주 작은 smoke를 돌릴 수 있는지"다.

### 준비 명령

PyTorch 공식 설치 기준에 맞춰 Python 3.10 이상 환경을 쓴다.

```bash
python3 -m venv .venv-vggt-mps
source .venv-vggt-mps/bin/activate
python -m pip install -U pip

python -m pip install torch torchvision torchaudio
python -m pip install numpy Pillow opencv-python scipy huggingface_hub

mkdir -p reference
git clone https://github.com/facebookresearch/vggt.git reference/vggt
python -m pip install -r reference/vggt/requirements.txt
python -m pip install -e reference/vggt
```

이미 `reference/vggt`가 있으면 `git clone`은 생략하고 `git -C reference/vggt pull --ff-only`로 최신화한다. `reference/`는 git에 커밋하지 않는다.

### 장치 확인

```bash
python - <<'PY'
import torch

print("torch:", torch.__version__)
print("mps built:", torch.backends.mps.is_built())
print("mps available:", torch.backends.mps.is_available())
PY
```

`mps available: True`가 나오면 로컬에서 1장 smoke를 시도할 수 있다. 일부 연산이 MPS에서 지원되지 않으면 다음 값을 임시로 켜서 CPU fallback을 확인할 수 있지만, 이 경우 속도는 크게 느려질 수 있다.

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

### 로컬에서 지킬 것

- 첫 입력은 대표 fixture 중 하나, 예를 들어 `laptop` 1장으로 제한한다.
- 2장 입력은 1장 성공 뒤에만 시도한다.
- 4장 이상은 기본 smoke로 잡지 않는다.
- checkpoint, `outputs/`, `.npz`, `.npy` 산출물은 커밋하지 않는다.

## 학교 NVIDIA RTX 30/40 Series

### 목적

학교 GPU는 실제 VGGT inference의 기본 경로다. 여기서는 CUDA가 정상인지 확인한 뒤, VGGT prediction을 `geometry.npz`로 저장하고 downstream `prior_from_mask --geometry-npz`까지 이어 붙이는 것이 목표다.

### GPU 확인

```bash
nvidia-smi
```

확인할 것:

- GPU 이름이 RTX 30/40 series인지
- VRAM이 8GB, 12GB, 16GB, 24GB 중 어느 급인지
- 현재 다른 프로세스가 VRAM을 많이 점유하고 있는지
- driver가 설치된 CUDA wheel과 맞는지

### 준비 명령

PyTorch CUDA wheel은 학교 장비의 driver/CUDA 상황에 맞춰 고른다. 아래는 CUDA 12.8 wheel 예시다. 실패하면 PyTorch 공식 설치 selector에서 해당 장비에 맞는 CUDA wheel을 다시 고른다.

PyTorch 공식 설치 기준에 맞춰 Python 3.10 이상 환경을 쓴다.

```bash
python3 -m venv .venv-vggt-cuda
source .venv-vggt-cuda/bin/activate
python -m pip install -U pip

python -m pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
python -m pip install numpy Pillow opencv-python scipy huggingface_hub

mkdir -p reference
git clone https://github.com/facebookresearch/vggt.git reference/vggt
python -m pip install -r reference/vggt/requirements.txt
python -m pip install -e reference/vggt
```

### CUDA 확인

```bash
python - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
    print("memory_gb:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
PY
```

`cuda available: True`가 나와야 실제 VGGT smoke를 진행한다.

### 학교 GPU에서 지킬 것

- RTX 4070 12GB급이면 1장으로 시작하고 2-4장까지만 늘린다.
- 8GB급이면 1장 smoke를 우선 성공 기준으로 둔다.
- 16GB 이상이면 4장 smoke 뒤 8-10장까지 확장 후보로 본다.
- 처음부터 수십 장 입력이나 큰 원본 이미지를 넣지 않는다.
- batch를 키우기보다 이미지 수를 줄이고, 필요하면 resize된 입력으로 먼저 확인한다.

## 우리 파이프라인과 연결하는 흐름

현재 repo에는 VGGT raw prediction을 `geometry.npz`로 저장하는 adapter와 `vggt_geometry` CLI skeleton이 있다. 기본 test suite는 fake runner로 검증하므로 VGGT dependency가 없어도 통과한다. 실제 smoke는 VGGT가 설치된 로컬 MPS 또는 학교 CUDA 환경에서 아래 명령으로 시도한다.

```bash
PYTHONPATH=src python -m object3d.pipeline.generate_smoke_fixtures \
  --output-dir outputs/representative-smoke-fixtures

PYTHONPATH=src python -m object3d.pipeline.vggt_geometry \
  --image-path outputs/representative-smoke-fixtures/laptop/image.png \
  --output-path outputs/vggt-smoke/laptop/geometry.npz \
  --device cuda
```

실제 VGGT smoke가 `outputs/vggt-smoke/laptop/geometry.npz`를 만들면, 기존 downstream은 그대로 이어진다.

VGGT가 내부에서 이미지를 resize/crop할 수 있으므로, segmentation mask와 depth map의 해상도가 다를 수 있다. `prior_from_mask`는 이 경우 mask를 geometry depth shape에 맞춰 nearest-neighbor로 자동 resize하고, summary에 `mask_alignment`, `input_mask_shape`, `geometry_depth_shape`, `effective_mask_shape`를 기록한다.

```bash
PYTHONPATH=src python -m object3d.pipeline.segment_image \
  --backend manual \
  --image-path outputs/representative-smoke-fixtures/laptop/image.png \
  --prompt-json outputs/representative-smoke-fixtures/laptop/prompt.json \
  --output-dir outputs/vggt-smoke/laptop/segmentation \
  --object-id laptop_001

PYTHONPATH=src python -m object3d.pipeline.prior_from_mask \
  --segmentation-summary outputs/vggt-smoke/laptop/segmentation/summary.json \
  --output-dir outputs/vggt-smoke/laptop/prior \
  --geometry-npz outputs/vggt-smoke/laptop/geometry.npz
```

## 다음 T에서 확인할 것

- VGGT dependency가 있는 환경에서 `vggt_geometry` CLI가 실제 checkpoint를 내려받고 inference를 완료하는지 확인
- 입력 이미지 1장을 VGGT prediction으로 바꾸고 `save_vggt_geometry_npz(...)`에 연결되는지 확인
- 로컬 MPS와 CUDA 장비를 모두 지원하되, default smoke는 1장으로 유지
- 성공 시 PR에는 `geometry.npz` 자체가 아니라 overlay/contact sheet 같은 작은 검증 이미지와 요약만 포함

## Rerun 환경 분리

최신 `rerun-sdk`는 `numpy>=2`를 요구하고, 현재 VGGT package는 `numpy<2`를 요구한다. 따라서 같은 venv에 섞지 않는다.

```bash
/opt/homebrew/bin/python3.11 -m venv .venv-rerun
.venv-rerun/bin/python -m pip install -U pip
.venv-rerun/bin/python -m pip install rerun-sdk numpy
```

보기:

```bash
.venv-rerun/bin/rerun outputs/.../scene.rrd
```

또는 spawn:

```bash
PATH="$PWD/.venv-rerun/bin:$PATH" PYTHONPATH=src .venv-rerun/bin/python -m object3d.visualization.view_scene \
  --manifest outputs/.../scene_manifest.json \
  --backend rerun \
  --spawn
```

## 참고 공식 문서

- [VGGT official repository](https://github.com/facebookresearch/vggt)
- [PyTorch install selector](https://pytorch.org/get-started/locally/)
- [PyTorch MPS backend notes](https://docs.pytorch.org/docs/stable/notes/mps.html)
- [NVIDIA GeForce RTX 40 series](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/)
