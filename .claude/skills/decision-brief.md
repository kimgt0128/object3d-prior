# Decision Brief 스킬

## 목적

멀티에이전트 conflict를 사용자가 결정할 수 있는 명확한 선택지로 제시한다.

## 사용할 때

- 두 agent가 호환되지 않는 contract를 제안한다.
- PR conflict가 단순 git merge를 넘어선다.
- model stack, dataset, GPU, folder structure, scope trade-off가 있다.
- reviewer 의견이 갈리고 증거만으로 결론이 나지 않는다.

## 사용하지 않을 때

- 단순 formatting 문제다.
- 기존 프로젝트 규칙이 명확히 해결한다.
- scope, architecture, risk 변화 없이 orchestrator가 안전하게 선택할 수 있다.

## brief 형식

```markdown
## 결정 필요

### 충돌

### 선택지 A
- 장점:
- 비용:
- 위험:
- 되돌릴 수 있는가:

### 선택지 B
- 장점:
- 비용:
- 위험:
- 되돌릴 수 있는가:

### 추천

### 선택 후 진행할 작업
```

## 절차

1. conflict를 한 문장으로 설명한다.
2. 실제 가능한 선택지만 제시한다.
3. 각 선택지에 장점, 비용, 위험, 되돌릴 수 있는지를 적는다.
4. 증거가 충분하면 하나를 추천한다.
5. 사용자가 선택하기 전에는 병합, 재작성, 삭제를 계속하지 않는다.

## 출력

위 brief 형식을 사용한다. 실제로 가능한 경우가 아니라면 숨은 세 번째 선택지를 만들지 않는다.
