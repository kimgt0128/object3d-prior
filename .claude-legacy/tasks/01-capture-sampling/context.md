# 컨텍스트 스냅샷

## 현재 상태

T1(capture) 셋업 단계. Issue draft·task folder·worker brief 확정 완료. worktree 미생성, 구현 미착수.

## 관련 파일

- 계획: `.claude/plans/ref/2026-05-20-first-mvp-detail-plan.md`
- Issue draft: `.claude/issues/001-capture-frame-sampling.md`
- worker brief: `workers/data-capture/brief.md`
- 생성 대상: `src/object3d/capture/`, `configs/capture.yaml`, `configs/default.yaml`, `tests/capture/`

## 결정된 사항

- T1 write scope = capture 모듈 4개 경로로 한정.
- `configs/default.yaml`은 T1이 생성·고정.
- 코드·테스트는 합성 영상 fixture 기반.

## 열린 질문

- 실제 스마트폰 영상 확보 시점 (capture-protocol 별도 산출물).
- frame sampling rate 기본값 — `configs/capture.yaml`에서 설정 가능하게 둔다.

## 읽지 말 것

- `cv_tutorial/`, `reference/`, `project/` 전체.
- 다른 task 폴더.

## 다음 작업

사용자 승인 후 worktree 생성 → data-capture worker dispatch.
