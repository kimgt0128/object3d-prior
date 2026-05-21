# Worker Brief: data-capture

## 대상 저장소

`computer_vision` — `main` 기준 worktree `feat/1-capture-sampling`

## 작업 폴더

`.claude/tasks/01-capture-sampling/`

## Issue

GitHub [#1](https://github.com/kimgt0128/object3d-prior/issues/1) (contract 원본: `.claude/issues/001-capture-frame-sampling.md`)

## 목표

스마트폰 영상에서 일정 간격 frame을 추출하고 `FrameRecord` 기반 frame manifest와 capture metadata를 생성한다.

## 입력

- 합성 영상 fixture (테스트용, 직접 생성)
- 객체 수동 실측값 W/D/H cm, camera mode, 조명, 재질 (`configs/capture.yaml`에 기록)

## 작성 가능 범위

- `src/object3d/capture/**`
- `configs/capture.yaml`
- `configs/default.yaml`
- `tests/capture/**`

## 작성 금지 파일

- `adapters/`·`geometry/`·`reconstruction/`·`priors/`·`evaluation/`·`visualization/` 전체
- root `README.md`, `src/README.md`
- 다른 task의 config

## 필수 스킬

`capture-protocol`, `anti-pattern-check` (구현 전 anti-pattern 확인)

## 기대 출력

- frame 추출 코드 + `FrameRecord` 스키마(frame_id, image_path, timestamp, camera_metadata)
- frame manifest 파일
- `configs/capture.yaml`(sampling rate, video path, object metadata), `configs/default.yaml`(top-level config)
- TDD 순서: 실패 테스트 → 최소 구현 → 통과 → 커밋 후보

## 검증

- unit test: 샘플링 간격 계산, `FrameRecord` 직렬화/역직렬화
- smoke test: 합성 fixture → manifest 생성
- 재현성: 같은 입력·config → 같은 manifest

## 인계 위치

`workers/data-capture/result.md` + handoff 블록. manifest 경로를 T2·T3에 넘긴다.
