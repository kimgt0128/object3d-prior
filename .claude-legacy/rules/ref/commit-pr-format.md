# 커밋과 PR 상세 형식

이 파일은 commit/PR 텍스트의 상세 형식과 예시를 담는 참고 문서다. 반복 적용되는 git 판단 기준은 `rules/git.md`가 canonical이며, 이 문서는 그 형식 세부를 보충한다.

각 domain agent는 하나의 coherent change 후보와 검증 근거를 남기고, 실제 staging, commit, PR 문구 정리는 Git Manager가 소유한다.

## 적용 범위

루트 `.gitignore`는 `project/`, `reference/`, `cv_tutorial/`를 추적에서 제외한다. 이 형식은 git이 추적하는 코드와 문서를 커밋할 때 적용한다.

## 언어 규칙

GitHub에 보이는 텍스트는 기본적으로 한글로 작성한다.

- commit subject
- commit body
- commit footer
- PR title
- PR body
- PR review comment
- merge 또는 conflict report

기술 식별자, branch name, file path, command, model name, issue reference는 원문을 유지한다.

## 커밋 메시지 형식

다음 한글 conventional 형식을 사용한다.

```text
type(#issue): 한글 요약

본문:
- 변경 내용:
- 변경 이유:
- 검증:

푸터(선택):
- 관련 이슈:
- 후속 작업:
```

허용 type:

- `feat`: 새로운 사용자 기능 또는 파이프라인 기능
- `fix`: 잘못된 동작 또는 누락된 필수 동작 수정
- `docs`: 문서만 변경
- `test`: 테스트 또는 fixture
- `refactor`: 동작 변화 없는 내부 구조 개선
- `perf`: 속도 또는 메모리 개선
- `chore`: 도구, 설정, 의존성, 유지보수
- `build`: 패키징 또는 환경 구성

예시:

```text
feat(#3): 세션 시간 조정

본문:
- 로그인 세션 유지 시간을 사용자 흐름에 맞게 조정
- 만료 기준을 설정 값으로 분리
- 관련 테스트와 수동 로그인 흐름을 확인

푸터:
- Resolves #3
```

```text
docs(#7): 멀티에이전트 라우팅 문서 정리
```

## Issue 제목 형식

Issue 제목은 prefix 없이 평문 한글로 쓴다. `[Feat]` 같은 type prefix를 붙이지 않는다.

```text
<한글 요약>
```

예시:

```text
T1: 입력 영상 프레임 샘플링 파이프라인
```

## PR 제목 형식

`[Type/<issue>-<branch>]: 한글 요약` 형식은 **PR 제목에만** 쓴다. Issue 제목에는 쓰지 않는다.

```text
[Type/<issue>-<branch>]: 한글 요약
```

예시:

```text
[Fix/3-login]: 전체적인 로그인 로직 수정
[Feat/12-object-prior]: 객체 크기 측정 파이프라인 추가
[Docs/7-agent-routing]: 멀티에이전트 라우팅 문서 정리
```

## PR 본문 형식

PR 본문은 한글로 작성한다.

```markdown
## 요약

## 변경 내용

## 검증

## 관련 이슈

## 리뷰 포인트

## 한계 및 후속 작업
```

Issue를 완전히 해결하는 PR에만 `Closes #<issue>`를 사용한다. 일부 작업이면 `Related #<issue>`를 사용한다.

## 커밋 경계 규칙

다음 중 하나가 충족될 때 커밋한다.

- pipeline stage의 입력/출력 contract가 동작한다.
- 테스트 가능한 utility가 완성됐다.
- 시각 검증 artifact가 만들어졌다.
- failure 또는 learning이 문서화됐다.
- config/model adapter 변경이 독립적이고 되돌릴 수 있다.

관련 없는 관심사를 섞지 않는다.

- segmentation과 geometry 변경을 한 커밋에 섞지 않는다. 단, integration commit은 예외다.
- 코드와 큰 data file을 함께 커밋하지 않는다.
- raw video, checkpoint, secret, generated cache를 커밋하지 않는다.
- 명시적으로 failing baseline을 기록하는 경우가 아니면 반쯤 깨진 실험을 커밋하지 않는다.

## 에이전트 커밋 후보 계약

커밋 전 domain agent는 다음을 기록하고 Git Manager에게 넘긴다.

- 무엇을 바꿨는지
- 왜 바꿨는지
- 어떻게 검증했는지
- 알려진 한계
- 다음 handoff

## 스택 브랜치 패턴

큰 작업은 작은 의존 브랜치로 나눈다.

```text
main
  -> feat/capture-protocol
    -> feat/sam2-tracking
      -> feat/object-pointcloud
        -> feat/object-measurement
```

각 브랜치는 독립적으로 리뷰 가능해야 한다. 나중에 Graphite `gt` 또는 GStack-style workflow를 설치하면 각 브랜치를 하나의 review unit으로 매핑한다.

## 커밋 전 체크리스트

- 테스트 또는 시각 검증 완료
- secret 또는 model checkpoint 미포함
- 관련 없는 generated file 미포함
- 문제를 해결하거나 새로 발견했다면 failure note 갱신
- architecture가 바뀌었다면 `PROJECT.md` 또는 관련 project docs 갱신
- commit과 PR 텍스트를 한글로 작성
