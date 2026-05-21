# MCP 및 외부 도구 메모

이 폴더는 외부 도구와 모델 연동 후보를 정리한다.

## 현재 입장

처음부터 복잡한 MCP 구성을 만들지 않는다. MVP가 동작한 뒤 반복되는 작업만 도구화한다.

## 가능성이 높은 외부 기능

- GitHub Issue와 PR 조회
- PR review comment 작성
- model checkpoint와 dataset 위치 관리
- 실험 결과 요약
- demo artifact 업로드

## 추적할 모델 연동

- SAM 계열 segmentation/tracking
- MapAnything 또는 VGGT geometry output
- COLMAP baseline
- Rerun 또는 Open3D visualization

## 연동 규칙

외부 도구 output은 project-owned normalized contract로 변환한 뒤 downstream에 넘긴다.
