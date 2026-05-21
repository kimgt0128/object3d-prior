# 객체 인식 3D 공간 보조 프로젝트

## LLM 최초 진입점

이 디렉터리는 컴퓨터 비전 프로젝트를 진행하는 모든 LLM 에이전트가 공유하는 계획 컨텍스트다.

구현 코드를 읽기 전에 반드시 이 파일부터 읽는다.

프로젝트 폴더 전체를 한 번에 읽지 않는다. 이 파일을 읽은 뒤 `agents/routing/command-router.md`를 읽고, 선택된 에이전트 파일과 스킬 파일만 추가로 읽는다. 자세한 참고 문서는 필요할 때만 연다.

Claude Code 세션은 repository root의 `CLAUDE.md`가 자동 로드되며, 그 지침이 이 파일과 `agents/routing/command-router.md`로 안내한다. 메인 세션이 Orchestrator 역할을 맡고, 자동 발동 가능한 네이티브 서브에이전트는 `.claude/agents/`에 있다.

## 경로 해석 규칙

이 문서 묶음의 기준 폴더는 repository root의 `.claude/`다. 이전 구조의 원본은 `project/`에 백업으로 남아 있으나 운영 기준은 `.claude/`다.

- 채팅이나 문서에서 `agents/...`, `skills/...`, `rules/...`, `plans/...`처럼 쓰인 경로는 `.claude/` 내부 상대 경로로 해석한다.
- 터미널에서 repository root(`/Users/kimgt/Developer/Project/computer_vision`) 기준으로 열 때는 `.claude/agents/...`처럼 `.claude/` prefix를 붙인다.
- 이미 `.claude/...`로 시작하는 경로는 repository root 기준 경로다. 긴 참조·상세는 각 영역의 `ref/` 폴더(`agents/ref/`, `rules/ref/`, `plans/ref/`)에 둔다.
- `README.md`, `src/README.md`, `.gitignore`처럼 root에 있는 공개 파일은 repository root 기준 경로다.
- 경로가 애매하면 추측하지 말고 `rg --files --no-ignore`로 실제 파일 존재 여부를 확인한다.

## 프로젝트 요약

최신 SAM 계열 세그멘테이션 모델을 단순한 2D 마스크 도구가 아니라 3D 객체 prior 생성기로 활용하는 실용적인 컴퓨터 비전 시스템을 만든다. SAM 마스크를 depth, camera pose, point cloud와 결합해 객체 단위 3D 정보로 끌어올리는 것이 핵심이다.

처음 목표는 방 전체 3D 복원이 아니다. 첫 번째 안정적인 마일스톤은 다음이다.

> 스마트폰 영상 속 실제 객체 하나를 추적하고, 객체 단위 3D point cloud를 복원하며, 실제 크기와 방향을 추정하고, 간단한 배치 가능성을 판단한다.

## 핵심 주장

이 프로젝트는 SAM 계열 모델을 object prior 생성기로 사용한다.

- 2D mask: 각 프레임에서 객체가 어디에 있는지
- video tracking: 같은 객체가 프레임 사이에서 일관되게 유지되는지
- text/concept prompt: 어떤 객체 범주를 선택했는지
- mask confidence: 객체 증거가 충분히 믿을 만한지
- 3D lifted prior: object point cloud, bounding box, orientation, scale, placement constraint

단순 세그멘테이션 데모보다 강한 이유는 SAM 출력이 3D 공간의 기하학적 제약으로 바뀌기 때문이다.

## 사용자에게 보여줄 데모

첫 데모는 다음 질문에 답할 수 있어야 한다.

- 이 객체의 대략적인 width, depth, height는 얼마인가?
- 이 객체는 방 좌표계에서 어디에 있는가?
- 이 객체는 어느 방향을 보고 있는가?
- 이 객체는 바닥에 붙어 있는가, 아니면 복원 노이즈 때문에 떠 있는가?
- 다른 box-like 객체를 이 공간에 배치할 수 있는가?
- 어떤 표면이 아직 관측되지 않아 추가 촬영이 필요한가?

## 현재 로컬 입력 자료

이미 저장소 안에 참고 자료가 있다.

- `cv_tutorial/`: 영상 처리, camera geometry, image correspondence, segmentation, classification, 3D vision을 다루는 강의 자료와 OpenCV 예제
- `reference/260328548v1_260520_111836.pdf`: visibility-guided 3D scene completion을 다루는 Seen2Scene 논문

이 자료들은 grounding으로 사용하되, 프로젝트 범위를 수업 내용에만 제한하지 않는다.

## 권장 기술 방향

### 기본 파이프라인

1. 스마트폰 영상에서 프레임을 추출한다.
2. SAM 계열 모델로 목표 객체를 세그멘트하고 추적한다.
3. MapAnything, VGGT 또는 다른 geometry 모델로 depth와 camera pose를 추정한다.
4. 마스크가 씌워진 픽셀만 3D point로 back-project한다.
5. 프레임 간 객체 point를 fusion한다.
6. 객체 단위 3D prior를 fitting한다.
   - oriented bounding box
   - center
   - dimensions
   - orientation
   - confidence
   - observed/unobserved surface hint
7. mask, camera path, object cloud, 3D box를 시각화한다.
8. 추정된 dimension을 수동 측정값과 비교한다.

### 처음부터 시작하지 말 것

- 첫 마일스톤으로 방 전체 dense reconstruction을 시도하지 않는다.
- Seen2Scene 전체 재현부터 시작하지 않는다.
- 대규모 3D 생성 모델 학습부터 시작하지 않는다.
- 단일 객체 MVP가 동작하기 전에 거대한 데이터셋을 내려받지 않는다.

이 항목들은 나중의 연구 확장으로 다룬다.

## 주요 기술 리스크

- pretrained 모델의 depth와 pose가 프레임마다 일관되지 않을 수 있다.
- COLMAP과 learned model의 scale convention이 다를 수 있다.
- 스마트폰 camera intrinsics와 lens distortion이 3D 복원을 휘게 만들 수 있다.
- SAM mask가 프레임 사이에서 jitter를 보이거나 배경을 포함할 수 있다.
- 투명, 반사, 얇은 물체, textureless 객체는 depth와 segmentation을 망가뜨릴 수 있다.
- 정답 3D geometry를 얻기 어렵기 때문에 평가를 수동 측정 가능한 물리 치수부터 시작해야 한다.

## 프로젝트 성공 기준

### MVP 성공 기준

- 객체 하나가 담긴 영상을 end-to-end로 처리할 수 있다.
- 선택된 프레임 사이에서 목표 객체가 일관되게 추적된다.
- 객체 단위 point cloud가 배경과 눈에 띄게 분리된다.
- box-like 또는 furniture-like 객체의 width, depth, height 추정값이 수동 측정값 대비 약 10-15% 이내다.
- Rerun 또는 Open3D 시각화에서 camera pose, object cloud, 3D bounding box가 명확히 보인다.

## 계획 문서

아래 파일을 기본적으로 전부 읽지 않는다. `agents/routing/command-router.md`로 필요한 문서만 선택한다.

- `agents/routing/command-router.md`: 명령을 에이전트와 스킬로 연결하는 라우터
- `agents/routing/routing-tree.md`: worker 선택 decision tree
- `agents/coordination/approval-policy.md`: 위험한 결정에 대한 사용자 승인 게이트
- `agents/coordination/orchestrator-rules.md`: Orchestrator 역할 규칙과 세션 시작 점검
- `agents/coordination/handoff-format.md`: 공통 인계(handoff) 형식
- `agents/ref/pr-orchestration.md`: PR·병합·conflict 상세 조율
- `agents/routing/routing-patterns.md`: 구체적 dispatch 다이어그램
- `agents/templates/`: task, context, worker brief, worker result, log 템플릿
- `tasks/README.md`: 작업별 상태 폴더 구조
- `rules/README.md`: git, 비즈니스 로직, 에이전트 운영, context, data, review, architecture 규칙
- `rules/business-logic.md`: 프로젝트 전역 anti-pattern과 중단 조건
- `agents/coordination/multi-agent-workflow.md`: Issue, worktree, PR, review comment, merge orchestration 흐름
- `plans/implementation-strategy.md`: 단계별 구현 전략
- `plans/ref/`: 길어진 계획과 단계별 상세 설명
- `rules/ref/commit-pr-format.md`: 커밋과 PR 작성 규칙
- `rules/ref/review-stack.md`: 기능 작업용 계층형 코드 리뷰 규칙
- `agents/README.md`: 에이전트 역할과 소유권 모델
- `agents/routing/assignment-matrix.md`: 실행 흐름별 에이전트/스킬 매핑
- `skills/README.md`: 재사용 가능한 작업 절차 목록
- `mcp/README.md`: 외부 도구와 모델 연동 메모
- `failures/README.md`: 실패 기록 프로토콜
- `agents/coordination/context-management.md`: 컨텍스트 로딩 정책
- `agents/coordination/context-memory.md`: 컨텍스트, 메모리, handoff 정책
- `agents/routing/flow-smoke-tests.md`: 라우팅 검증용 smoke test
- `rules/ref/future-code-layout.md`: 향후 실제 코드 모듈 구조 계획
- `plans/ref/model-concept-map.md`: 주요 모델과 공부할 개념 지도
- `agents/ref/recommended-workflow-resources.md`: 외부 참고 자료 목록

## 컨텍스트 로딩 규칙

- 모든 agent 파일을 읽지 않는다. 라우팅된 owner와 필요한 supporting agent만 읽는다.
- 모든 skill 파일을 읽지 않는다. `agents/routing/command-router.md`가 고른 skill만 읽는다.
- 모든 task 폴더를 읽지 않는다. 활성 `.claude/tasks/<task-name>/`만 읽는다.
- `cv_tutorial/`이나 `reference/`를 넓게 읽지 않는다. 먼저 검색하고 관련 파일만 연다.
- 도움이 될 것 같다는 이유만으로 컨텍스트를 계속 늘리지 않는다. 현재 작업이 막혔을 때만 더 읽는다.
- 문서가 길어지면 세부 내용은 해당 영역의 `ref/` 폴더로 옮기고 원래 파일은 index로 유지한다.
- 큰 출력은 채팅에 붙이지 말고 활성 task 폴더에 저장한 뒤 경로만 handoff한다.

## 에이전트 운영 규칙

- 항상 이 파일을 먼저 읽고, `agents/routing/command-router.md`로 사용자 요청을 라우팅한다.
- 작고 검증 가능한 마일스톤을 우선한다.
- 외부 모델 wrapper와 프로젝트 소유 geometry logic을 분리한다.
- pretrained 모델 출력은 정답이 아니라 noisy measurement로 취급한다.
- 모든 실험은 입력 데이터, 모델 버전, 파라미터, 결과 품질을 기록한다.
- 실패 사례를 숨기지 않는다. 실패 분석도 프로젝트 가치의 일부다.
- 테스트 또는 시각 검증이 끝난 coherent feature slice 단위로 커밋한다.
- 중요한 코드는 self-check, spec check, domain review, integration review 순서로 stacked review를 거친다.
- 해결된 실패는 다음 에이전트가 반복하지 않도록 durable note로 남긴다.
- 구현 작업은 Issue-first와 isolated worktree 실행을 기본으로 한다.
- 멀티에이전트 작업은 dispatch 전에 task folder와 compact worker brief를 만든다.
- PR이 있으면 리뷰 결과를 PR comment로 남긴다.
- PR 충돌이 있으면 조용히 선택하지 말고 사용자에게 선택지를 제시한다.
- 멀티에이전트 작업은 조율 비용이 작업 자체보다 커지지 않게 작게 유지한다.
