# Object3D Prior - Codex Entry Point

이 문서는 Codex가 이 프로젝트에 처음 들어왔을 때 읽는 **최소 진입점**이다.
자세한 프로젝트 설명은 `docs/README.md`를 기준으로 하고, 이 문서는 무엇을 읽고, 어떤 도구를 쓰고, 무엇을 하지 말아야 하는지 정하는 라우터 역할만 한다.

## 1. Project Overview

Object3D Prior는 SAM/SAM2 계열 모델의 2D segmentation mask를 depth, camera pose, point cloud와 결합해 3D object prior로 확장하는 컴퓨터 비전 프로젝트다.

첫 MVP는 방 전체 3D 복원이 아니라, **단일 객체 하나**를 대상으로 한다.

목표 흐름은 다음과 같다.

```text
video -> frame sampling -> object mask -> depth/pose contract
-> masked back-projection -> object point cloud fusion
-> oriented bbox / dimensions / confidence -> evaluation / visualization
```

기본 전략은 **No-Training First**다. 먼저 pretrained model, mock adapter, geometry pipeline을 조합해 end-to-end 흐름을 만든 뒤, 실제 병목이 확인될 때만 학습, fine-tuning, 자동화를 추가한다.

## 2. Directory Routing

항상 먼저 읽는다.

- `PROJECT.md`
- `docs/README.md`

필요할 때만 선택적으로 읽는다.

- `src/README.md`: 코드 구조나 모듈 경계를 확인할 때
- `docs/PLAN.md`: 현재 구현 계획이나 다음 작업 순서를 확인할 때
- `.serena/project.yml`: Serena 설정이나 코드 분석 MCP 문제가 있을 때
- `project/commands/git.md`: 자주 쓰는 Git 명령 흐름을 확인할 때
- `project/mcp/README.md`: MCP 사용 원칙이나 Serena 설정 흐름을 확인할 때
- `project/skills/README.md`: 반복 행동을 skill로 승격할지 판단할 때
- `cv_tutorial/`: 수업 자료와 연결해야 할 때
- `reference/`: 논문이나 외부 레퍼런스를 확인해야 할 때
- `docs/superpowers/`: Superpowers가 생성한 과거 설계나 계획이 필요할 때

기본 작업에서는 읽지 않는다.

- `project/`: 로컬 하네스 메모다. 사용자가 요청한 하위 문서만 선택적으로 읽는다.
- `.claude/`: Claude 전용 설정이다. Codex 작업에서는 기본적으로 읽지 않는다.

무차별 전체 폴더 읽기를 피하고, 현재 요청에 필요한 문서와 코드만 선택적으로 읽는다.

## 3. Skill Routing

### Serena

Serena는 코드 분석 핵심 MCP로 사용한다.

반드시 Serena 사용을 우선 고려해야 하는 경우:

- public interface 변경 전
- 큰 리팩터링 전
- PR 리뷰 전
- 주요 symbol의 참조 범위를 확인해야 할 때
- 코드 구조를 처음 파악해야 하는데 전체 파일 읽기가 비효율적일 때

Serena를 강제하지 않는 경우:

- 문서 수정
- GitHub 템플릿 수정
- 단순 설정 확인
- 단일 파일의 작은 수정

### Superpowers

Superpowers는 필요한 경우에만 최소로 사용한다.

- 새 기능이나 큰 설계 전: `brainstorming`
- 승인된 설계를 구현 계획으로 바꿀 때: `writing-plans`
- 완료를 주장하기 전: `verification-before-completion`

현재 실행 계획은 `docs/PLAN.md` 하나로 유지한다. Superpowers가 만든 과거 산출물은 필요할 때만 `docs/superpowers/` 아래에서 선택적으로 읽는다.

같은 행동이 3번 이상 반복되면 skill 생성을 제안하되, 추가 전에는 사용자 승인을 받는다.

## 4. Core Rules

큰 기능 구현 흐름:

1. GitHub Issue를 먼저 만든다.
2. 해당 Issue에서 branch를 생성한다.
3. branch 안에서는 세부 단위별로 커밋한다.
4. 큰 기능 단위가 끝나면 PR을 올린다.
5. PR에는 변경 요약, 관련 이슈, 검증 결과, 리뷰 포인트, 주의사항을 한글로 적는다.

작은 문서 수정, 오타 수정, 단순 설정 확인은 Issue 없이 처리할 수 있다.

기능 구현, 구조 변경, 리팩터링, 데이터 파이프라인 변경은 Issue-first 흐름을 따른다.

커밋 메시지는 한글로 작성한다.

```text
<type>(#issue): <요약>
```

예시:

```text
feat(#3): 프레임 샘플링 파이프라인 추가
fix(#7): 마스크 후처리 임계값 오류 수정
docs(#2): 프로젝트 목적 문서 보강
refactor(#5): GeometryRecord 인터페이스 분리
test(#6): bbox 크기 측정 테스트 추가
```

PR 제목 예시:

```text
[Feat/3-frame-sampling]: 프레임 샘플링 파이프라인 추가
```

## 5. Verification

완료를 주장하기 전에 요청 범위에 맞는 검증을 수행한다.

- 코드 변경: 관련 테스트, lint, smoke test 중 가능한 것을 실행한다.
- geometry 변경: 좌표계, scale, shape, 단위가 깨지지 않았는지 확인한다.
- interface 변경: Serena로 참조 범위를 확인한다.
- visualization 변경: 결과 이미지, point cloud, bbox가 비어 있거나 뒤틀리지 않았는지 확인한다.
- 문서 변경: 링크, 경로, 현재 프로젝트 상태와 모순이 없는지 확인한다.

검증하지 못한 항목은 최종 답변에 명확히 적는다.

## 6. Do Not

- 요청 없이 대형 하네스 구조를 만들지 않는다.
- 전체 폴더를 무차별로 읽지 않는다.
- `project/`, `reference/`, `cv_tutorial/`, `docs/superpowers/`는 필요할 때만 선택적으로 읽는다.
- 사용자가 만들었을 가능성이 있는 변경사항을 되돌리지 않는다.

## 7. Documentation Policy

문서 역할은 다음처럼 나눈다.

- `PROJECT.md`: Codex 전용 최초 진입점과 작업 방식
- `docs/README.md`: 서비스 목적, 아키텍처, MVP 설명
- `docs/PLAN.md`: 현재 실행 계획
- `src/README.md`: 코드 구조와 실행 방식
- `docs/superpowers/`: 필요한 경우에만 참고하는 과거 상세 설계와 계획

`PROJECT.md`는 항상 200줄 이하로 유지한다. 세부 설명이 길어지면 `docs/` 아래 상세 문서로 분리하고, 이 문서에는 링크와 읽는 조건만 남긴다.

## 8. Coding Conventions

현재는 과한 코드 규칙을 두지 않는다.

기본 원칙:

- 기존 코드 스타일을 우선 따른다.
- public record/interface는 downstream 사용자가 이해할 수 있게 명확히 유지한다.
- raw model output을 downstream에 그대로 흘리지 말고 adapter에서 표준 record로 변환한다.
- 좌표계, scale, 단위는 코드와 문서에 명확히 남긴다.
- 데이터, 모델 가중치, 시각화 산출물은 Git에 커밋하지 않는다.

세부 convention이 반복적으로 필요해지면 그때 별도 문서로 분리한다.

## 9. Architecture Summary

첫 MVP의 핵심 모듈은 다음이다.

- Capture: 입력 영상과 프레임 샘플링
- Segmentation Adapter: SAM/SAM2 mask를 표준 `MaskRecord`로 변환
- Geometry Adapter: depth, intrinsics, pose를 표준 geometry record로 변환
- Geometry: masked back-projection
- Reconstruction: object point cloud fusion
- Priors: oriented bbox, dimensions, orientation, confidence 추정
- Evaluation: 실측값 대비 오차와 실패 원인 기록
- Visualization: Open3D/Rerun 기반 결과 확인

자세한 목적과 단계 설명은 `docs/README.md`를 따른다.

## 10. Response Policy

기본 답변은 한글로 한다. 코드 식별자, 파일명, 라이브러리명, 명령어는 원문을 유지한다.

작업 중 충돌 가능성이 있거나 설계 선택지가 있으면 임의로 결정하지 말고 선택지를 제시한다.

단순 질문에는 짧게 답하고, 구현 요청에는 필요한 범위만 확인한 뒤 실행한다.

현재 프로젝트의 핵심 운영 원칙은 **필요한 만큼만 읽고, 필요한 만큼만 자동화하고, 실패가 반복될 때만 하네스를 확장하는 것**이다.
