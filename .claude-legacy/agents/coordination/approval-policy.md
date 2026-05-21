# 공용 승인 정책

계속 진행하기 전에 사용자 결정이 필요한 경우 이 파일을 사용한다.

## 승인 게이트

다음 작업 전에는 사용자 승인을 받는다.

- architecture 또는 folder ownership 변경
- model stack 방향 변경
- 큰 dataset 또는 checkpoint 다운로드
- GPU training 시작
- branch, file, generated asset, worktree 삭제
- 다른 agent의 작업을 버리는 방식으로 PR conflict 해결
- unresolved review finding이 있는 PR 병합

## 승인 없이 진행 가능한 작업

다음은 별도 승인 없이 진행할 수 있다.

- local task folder 생성
- local issue draft 작성
- 기존 범위 안의 planning doc 수정
- 작은 template 또는 routing clarification 추가
- read-only inspection 실행

## 결정 형식

선택지가 의미 있는 경우 `.claude/skills/decision-brief.md`를 사용한다.

trade-off를 문장 속에 숨기지 않는다. option, recommendation, next action을 분리해 제시한다.
