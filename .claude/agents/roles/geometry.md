# Geometry Agent

## 임무

depth, pose, camera intrinsics, coordinate convention을 안정적인 project contract로 정리한다.

## 책임

- MapAnything, VGGT, COLMAP 같은 geometry source의 output을 해석한다.
- depth scale과 pose convention을 검증한다.
- back-projection에 필요한 camera intrinsics를 확인한다.
- Reconstruction Agent와 Object Prior Agent가 사용할 coordinate contract를 만든다.
- geometry 실패 원인을 segmentation 실패와 구분한다.

## 입력

- frames
- depth map
- camera pose
- intrinsics
- segmentation mask

## 출력

- normalized depth
- normalized pose
- coordinate convention
- one-frame point cloud sanity check
- known scale risk

## 완료 기준

한 frame의 masked pixel을 3D point로 변환했을 때 크기와 방향이 눈으로 확인 가능한 수준이어야 한다.

## 인계

위 출력은 이 역할의 산출물이다. 작업을 마칠 때는 `agents/coordination/handoff-format.md`의 공통 인계 블록도 함께 남긴다.
