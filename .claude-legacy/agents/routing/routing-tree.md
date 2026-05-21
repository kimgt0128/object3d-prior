# 공용 라우팅

이 파일은 worker 선택을 위한 짧은 decision tree다. 자세한 판단이 필요하면 `.claude/agents/routing/command-router.md`를 기준으로 삼는다.

## 경로 기준

이 문서의 agent와 skill 경로는 `.claude/` 기준이다. repository root에서 열 때는 `.claude/agents/...`, `.claude/skills/...`처럼 연다.

## 라우팅 decision tree

1. 계획 요청이면 Research Agent와 Integration Agent를 사용한다.
2. 구현이 시작되면 Issue Manager Agent, Git Manager Agent, domain owner 순서로 진행한다.
3. 촬영, capture, 영상 수집, 실측값이면 Data and Capture Agent를 사용한다.
4. SAM, mask, prompt, tracking이면 Segmentation Agent를 사용한다.
5. depth, pose, camera, intrinsics, scale이면 Geometry Agent를 사용한다.
6. point cloud, fusion, TSDF, back-projection이면 Reconstruction Agent를 사용한다.
7. bbox, dimension, orientation, placement이면 Object Prior Agent를 사용한다.
8. metric, ablation, data analysis면 Evaluation Agent를 사용한다.
9. Rerun, Open3D, Gradio, screenshot, demo evidence면 Visualization Agent를 사용한다.
10. git, branch, commit, worktree, PR mechanics면 Git Manager Agent를 사용한다.
11. review 요청이면 Review Orchestrator Agent를 사용한다.
12. merge order 또는 conflict면 PR Merge Orchestrator Agent를 사용한다.
13. context, memory, token, compaction이면 Orchestrator가 주 담당, Structure Manager가 지원한다.
14. template, 파일 구조, 폴더 배치면 Structure Manager Agent를 사용한다.
15. 위 어느 항목에도 맞지 않으면 추측하지 말고 `command-router.md`로 분류하거나 사용자에게 확인한다.

## dispatch 방식

- 병렬 실행은 write scope가 겹치지 않을 때만 사용한다.
- 한 agent의 출력이 다른 agent의 입력이면 순차 실행한다.
- read-only research 또는 blocking이 아닌 review만 background로 둔다.

## 하지 말 것

- brief 없이 worker를 시작하지 않는다.
- worker가 task file보다 넓은 범위를 스스로 고르게 하지 않는다.
- Orchestrator가 integration task를 만들지 않은 상태에서 두 worker가 같은 artifact를 수정하게 하지 않는다.
