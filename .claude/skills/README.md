# 스킬

이 폴더는 프로젝트 로컬 작업 절차를 담는다. 전역 플러그인 스킬이 아니며, `agents/routing/command-router.md`가 선택한 경우에만 읽는다.

## 하지 말 것

- 세션 시작 시 모든 skill 파일을 읽지 않는다.
- 이름이 비슷하다는 이유만으로 skill을 사용하지 않는다.
- 긴 예시와 상세 설명은 영역별 `ref/`로 보낸다.
- skill이 primary owner를 바꾸게 하지 않는다. owner 결정은 라우터가 소유한다.

## skill 파일 계약

각 skill은 다음을 명확히 해야 한다.

- 목적: 왜 존재하는가
- 사용할 때: 어떤 요청에서 발동하는가
- 사용하지 않을 때: 언제 다른 owner나 skill이 더 맞는가
- 절차: 반복 가능한 짧은 단계
- 출력: 어떤 artifact 또는 결정을 남기는가

## skill index

| Skill | 목적 | 사용할 때 | 사용하지 않을 때 |
|---|---|---|---|
| `skills/command-routing.md` | 요청을 하나의 owner로 라우팅 | 새 요청이 들어왔을 때 | owner가 이미 명확한 이어지는 작업 |
| `skills/task-orchestration.md` | task folder와 worker brief 생성 | 멀티에이전트 작업 분해 | 단일 owner가 바로 처리 가능한 작업 |
| `skills/implementation-planning.md` | 전략을 phase 단위 작업으로 분해 | 계획, 로드맵, milestone 요청 | 사용자가 바로 구현을 요청한 경우 |
| `skills/anti-pattern-check.md` | 프로젝트 stop condition 확인 | 금지, risk, 실패 방지 요청 | 좁은 구현 변경 |
| `skills/context-memory-optimization.md` | 컨텍스트 낭비를 줄이고 handoff 보존 | context, memory, token, compaction 문제 | 단발성 설명 |
| `skills/issue-worktree-workflow.md` | Issue와 isolated worktree 준비 | 구현 작업을 agent에게 배정 | 논의만 하는 작업 |
| `skills/capture-protocol.md` | 좋은 입력 영상 수집 | 촬영 데이터 준비 | 이미 있는 output 디버깅 |
| `skills/model-adapter.md` | 외부 모델 output 정규화 | SAM, MapAnything, VGGT, COLMAP 추가 | 프로젝트 소유 geometry logic 작성 |
| `skills/geometry-validation.md` | depth, pose, point cloud 문제 진단 | geometry 결과가 이상할 때 | mask 품질 문제가 명확할 때 |
| `skills/object-prior-fitting.md` | mask와 geometry를 object prior로 변환 | bbox, dimension, orientation, placement 작업 | raw segmentation 또는 depth 추출만 할 때 |
| `skills/experiment-logging.md` | 실험 실행과 파라미터 기록 | 실험, ablation, threshold search | 정적 문서 작성 |
| `skills/visual-demo.md` | 데모와 보고서용 시각 근거 생성 | demo/report visualization | core pipeline logic 변경 |
| `skills/commit-protocol.md` | coherent slice 커밋 | 검증된 작업을 커밋할 때 | 리뷰 전이거나 unrelated file이 섞였을 때 |
| `skills/code-review-stack.md` | 계층형 리뷰 실행 | 구현 또는 구조 변경 리뷰 | risk 없는 작은 오타 수정 |
| `skills/pr-review-commenting.md` | PR에 리뷰 결과 게시 | PR이 있고 리뷰가 끝났을 때 | PR이 없거나 민감한 로컬 리뷰 |
| `skills/pr-merge-orchestration.md` | PR 병합 순서와 conflict 처리 | 여러 PR 또는 의존 PR이 있을 때 | 단일 trivial PR |
| `skills/decision-brief.md` | 사용자 결정이 필요한 선택지 제시 | conflict가 사람 판단을 요구할 때 | 규칙으로 바로 결정 가능한 경우 |
| `skills/failure-recording.md` | 실패와 삽질을 재사용 지식으로 저장 | non-obvious failure 또는 bugfix 발생 | 증거 없는 vague note |
| `skills/folder-structure-management.md` | 폴더 구조를 일관되게 유지 | 모듈/폴더 추가 또는 이동 | 기존 모듈 내부 코드만 수정 |
| `skills/git-management.md` | branch, commit, PR hygiene 관리 | git, branch, commit, PR 요청 | 구현만 요청한 경우 |
