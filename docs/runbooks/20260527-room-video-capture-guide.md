# Room Video Capture Guide

이 문서는 기말 프로젝트 smoke에 사용할 방 영상 하나를 어떻게 찍을지 정리한다.
목표는 예쁜 영상이 아니라, VGGT가 keyframe 사이의 구조와 카메라 이동을 잡기 쉬운
입력 영상을 만드는 것이다.

## 한 개 영상이면 충분한가

첫 smoke는 방 영상 하나로 충분하다. 좋은 기준은 30-60초, 천천히 움직이는
스마트폰 영상이다. 이후 결과가 부족하면 같은 방을 다른 높이나 반대 방향에서
찍은 두 번째 영상을 추가한다.

## 촬영 방법

- 방 중앙이나 입구 근처에서 시작한다.
- 180-360도 정도를 천천히 돈다.
- 책상, 노트북, 의자, 컵, 침대, 선반 같은 주요 물체를 각각 2-3초씩 여러 각도에서 보이게 한다.
- 흰 벽만 오래 찍지 말고, 모서리, 책상 edge, 포스터, 가구 경계처럼 특징점이 있는 부분을 포함한다.
- 너무 빠르게 팬하지 않는다.
- 줌은 고정하고, 가능하면 자동 초점이 크게 튀지 않게 찍는다.
- A4 용지, 자, 노트북처럼 실제 크기를 아는 물체 하나를 화면에 둔다.

## 좋은 입력 예시

- 작은 자취방이나 책상 주변을 천천히 둘러보는 영상
- 책상 위 물체와 방 벽/바닥/가구가 함께 보이는 영상
- 같은 물체가 최소 2-3개 keyframe에 다른 각도로 보이는 영상

## 피해야 할 입력

- 빠르게 좌우로 흔드는 영상
- 거의 전부 흰 벽이나 검은 소파처럼 특징점이 부족한 영상
- 너무 어두운 영상
- 투명 컵, 반사 화면, 빨대처럼 초기 성공 기준 밖의 물체만 강조한 영상
- 사람 얼굴, 민감한 문서, 개인정보가 크게 보이는 영상

## PR A 실행 예시

```bash
ROOM_VIDEO=/absolute/path/to/room-video.mov
RUN_DIR=outputs/room-video-pr-a

PYTHONPATH=src python -m object3d.pipeline.video_keyframes \
  --video-path "$ROOM_VIDEO" \
  --output-dir "$RUN_DIR/keyframes" \
  --manifest-path "$RUN_DIR/frame_manifest.json" \
  --target-fps 0.5
```

로컬 Mac MPS에서는 frame 수를 작게 시작한다.

```bash
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src python -m object3d.pipeline.vggt_geometry_batch \
  --manifest "$RUN_DIR/frame_manifest.json" \
  --output-dir "$RUN_DIR/geometry" \
  --device mps \
  --max-frames 8
```

학교 CUDA GPU에서는 16장 정도까지 올려서 시도한다.

```bash
PYTHONPATH=src python -m object3d.pipeline.vggt_geometry_batch \
  --manifest "$RUN_DIR/frame_manifest.json" \
  --output-dir "$RUN_DIR/geometry" \
  --device cuda \
  --max-frames 16
```

## Git 원칙

원본 영상, keyframe, VGGT `geometry.npz`, point cloud, Rerun recording은 커밋하지
않는다. PR에는 필요할 때 anonymized screenshot, contact sheet, validation markdown만
넣는다.
