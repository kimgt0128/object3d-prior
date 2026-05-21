# 라우팅 패턴

command router의 한 줄 route만으로 부족할 때만 이 파일을 연다.

## Pattern A: 새 기능

```mermaid
flowchart TD
    A["Orchestrator"] --> B["Domain Agent"]
    A --> I["Issue Manager"]
    I --> W["Independent Worktree"]
    W --> B
    B --> C["Evaluation Agent"]
    B --> D["Visualization Agent"]
    C --> E["Review Orchestrator"]
    D --> E
    E --> P["PR Review Comment"]
    P --> M["PR Merge Orchestrator"]
```

domain agent가 Issue 생성을 건너뛰거나 worktree 밖에 쓰지 않게 한다.

## Pattern B: 코드 리뷰

```mermaid
flowchart TD
    A["Orchestrator"] --> B["Review Orchestrator"]
    B --> C["Spec Compliance Layer"]
    B --> D["Domain Review Layer"]
    B --> E["Compound Review Layer"]
    C --> F["Findings"]
    D --> F
    E --> F
    F --> P["Post PR Comment if PR exists"]
    P --> G["Failure Recorder if recurring issue"]
    P --> H["PR Merge Orchestrator if merge affected"]
```

모호한 review summary를 올리지 않는다. blocking finding에는 파일, 동작, merge 영향이 있어야 한다.

## Pattern C: 폴더 구조 또는 아키텍처 정리

```mermaid
flowchart TD
    A["Orchestrator"] --> B["Structure Manager"]
    B --> C["Integration Agent"]
    C --> D["Review Orchestrator"]
    D --> E["PR Merge Orchestrator"]
```

파일을 옮길 때 routing, skill, import, reference를 함께 갱신한다.

## Pattern D: 실패 조사

```mermaid
flowchart TD
    A["Orchestrator"] --> B["Relevant Domain Agent"]
    B --> C["Failure Recorder"]
    C --> D["Evaluation Agent"]
    D --> E["Review Orchestrator if code changed"]
```

재현 단계, 관찰된 출력, 다음에 반복하지 말 시도를 남기지 않은 failure 기록은 만들지 않는다.
