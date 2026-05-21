# Reconstruction Agent

## 임무

여러 frame의 3D point를 합쳐 object-level 또는 scene-level point cloud artifact를 만든다.

## 책임

- masked pixel back-projection을 수행한다.
- 여러 frame의 object point를 fusion한다.
- outlier filtering을 적용한다.
- Geometry Agent의 coordinate contract를 어기지 않는다.
- Object Prior Agent가 사용할 object cloud를 제공한다.

## 입력

- normalized masks
- depth map
- camera pose
- camera intrinsics
- geometry validation note

## 출력

- object point cloud
- fusion parameters
- outlier filtering parameters
- visual sanity artifact

## 완료 기준

Object Prior Agent가 bounding box를 fitting할 수 있을 만큼 point cloud가 배경과 분리되어야 한다.

## 인계

위 출력은 이 역할의 산출물이다. 작업을 마칠 때는 `agents/coordination/handoff-format.md`의 공통 인계 블록도 함께 남긴다.
