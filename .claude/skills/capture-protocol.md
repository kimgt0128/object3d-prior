# Capture Protocol 스킬

## 목적

나쁜 입력 데이터 때문에 segmentation, geometry, measurement가 망가지지 않도록 촬영 조건을 관리한다.

## 사용할 때

객체 단위 3D 측정을 위한 스마트폰 영상 또는 이미지를 수집할 때 사용한다.

## 사용하지 않을 때

- 이미 촬영한 dataset을 디버깅하는 중이다.
- model threshold를 튜닝하는 중이다.
- git 또는 폴더 구조를 리뷰하는 중이다.

## 절차

1. 먼저 단순한 객체 하나를 고른다.
2. width, depth, height를 수동으로 측정한다.
3. 반사, 투명, 검은 glossy, 아주 얇은 객체를 피한다.
4. calibration이 없다면 ultra-wide가 아니라 일반 camera mode를 사용한다.
5. 객체 주변을 천천히 이동한다.
6. 영상 전체에서 객체가 보이게 유지한다.
7. 최소 세 면을 촬영한다.
8. placement reasoning이 필요하면 바닥 또는 테이블 접촉면을 포함한다.
9. motion blur와 갑작스러운 노출 변화를 피한다.
10. 기기, camera mode, 조명, 재질, 측정값을 기록한다.

## 출력

- raw video 저장 여부
- 수동 측정값
- 촬영 note
- prompt용 대표 frame
