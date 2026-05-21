# 작업: 01-capture-sampling (T1 입력 영상/프레임 샘플링)

상태: review

## 목표

스마트폰 영상에서 일정 간격 frame을 추출하고, `FrameRecord` 스키마 기반 frame manifest와 capture metadata를 만들어 T2(segmentation)·T3(geometry)가 재현 가능하게 쓰도록 한다.

## 제약

- write scope 밖 파일 수정 금지.
- 실제 모델 연동·mask·depth 금지 (T2 이후 단계).
- raw video, checkpoint를 git에 올리지 않는다.
- 코드·테스트는 합성 영상 fixture 기반으로 개발한다.

## 주 담당

Data and Capture Agent

## 예정 worker

data-capture (single worker)

## worker 승인 여부

yes  (2026-05-21 사용자 승인, worktree 생성 후 dispatch)

## 작성 가능 범위

- `src/object3d/capture/**`
- `configs/capture.yaml`
- `configs/default.yaml`
- `tests/capture/**`

## 작성 금지 파일

- `src/object3d/adapters/**`, `geometry/**`, `reconstruction/**`, `priors/**`, `evaluation/**`, `visualization/**`
- 다른 task의 config
- root `README.md`, `src/README.md` (T8 통합 시 갱신)

## 검증

- unit test: 샘플링 간격 계산, `FrameRecord` 직렬화/역직렬화
- smoke test: 합성 영상 fixture → frame manifest 생성
- 재현성: 같은 입력·config → 같은 manifest

## 승인 게이트

- worker dispatch 전 사용자 승인 필요 (현재 단계).
- 구현 후 self-check + test 통과 후 Git Manager 커밋.

## 현재 결정

- Issue: GitHub [#1](https://github.com/kimgt0128/object3d-prior/issues/1) (contract 원본: `.claude/issues/001-capture-frame-sampling.md`)
- branch: `feat/1-capture-sampling`
- worktree: `/Users/kimgt/Developer/Project/cv-feat-1-capture-sampling` (생성됨)
- commit: `f188a58` feat(#1) — 14파일, 833 insertions
- PR: GitHub [#2](https://github.com/kimgt0128/object3d-prior/pull/2) (`Closes #1`, 리뷰 대기)
