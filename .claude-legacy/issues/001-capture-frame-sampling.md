# Issue 001: 입력 영상 프레임 샘플링 파이프라인

> 2026-05-21 GitHub Issue로 승격됨 → [kimgt0128/object3d-prior#1](https://github.com/kimgt0128/object3d-prior/issues/1). 구현 PR [#2](https://github.com/kimgt0128/object3d-prior/pull/2) (`Closes #1`). 이 파일은 contract 원본으로 유지한다.

## 요약

스마트폰 영상에서 일정 간격으로 frame을 추출하고, downstream(segmentation·geometry)이 재현 가능하게 사용할 frame manifest와 capture metadata를 만든다. No-Training MVP의 T1이다.

## Issue contract

- **Issue:** [GitHub #1](https://github.com/kimgt0128/object3d-prior/issues/1) — 입력 영상 프레임 샘플링 파이프라인
- **작업 폴더:** `.claude/tasks/01-capture-sampling/`
- **담당:** Data and Capture Agent (주 담당) / Orchestrator (조율) / Issue Manager (Issue contract)
- **범위:**
  - 영상에서 일정 간격 frame 추출
  - `FrameRecord` 스키마 기반 frame manifest 생성
  - capture metadata(객체명, 수동 실측값 W/D/H cm, camera mode, 조명, 재질) 기록
  - capture protocol checklist 정리
- **비목표:**
  - segmentation·mask (T2)
  - depth·pose (T3)
  - back-projection 이후 모든 단계 (T4~T8)
  - 실제 모델 연동
- **허용 파일:** `src/object3d/capture/**`, `configs/capture.yaml`, `configs/default.yaml`, `tests/capture/**`
- **worktree branch:** `feat/1-capture-sampling` (`main` 기준)
- **예상 PR:** `[Feat/1-capture-sampling]: 입력 영상 프레임 샘플링 파이프라인 추가`
- **검증:**
  - unit test: 샘플링 간격 계산, `FrameRecord` 직렬화/역직렬화
  - smoke test: 합성 영상 fixture → frame manifest 생성
  - 재현성: 같은 입력·config로 같은 manifest

## 충돌 위험

- write scope가 capture 모듈로 한정되어 T2~T8과 겹치지 않는다.
- `configs/default.yaml`은 T1이 생성·고정한다. 이후 작업은 자기 모듈 config만 추가한다(공유 파일 규칙).

## 열린 의존성

- 실제 스마트폰 영상이 아직 없다. 코드·테스트는 합성 영상 fixture로 개발하고, 실제 촬영 영상은 capture-protocol 산출물로 별도 확보한다.
