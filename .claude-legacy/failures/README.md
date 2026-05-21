# 실패 기록

이 폴더는 재사용 가능한 실패 기록을 저장한다.

## 추가할 때

다음 경우 기록한다.

- model output이 misleading했다.
- geometry convention 또는 scale 문제를 찾아냈다.
- threshold search로 중요한 제약을 발견했다.
- debugging 과정이 non-obvious였다.
- 다음 agent가 같은 시도를 반복할 위험이 있다.

## 이름 규칙

```text
YYYY-MM-DD-short-slug.md
```

## 최소 내용

- 증상
- 입력과 환경
- 시도한 방법
- 실패 이유
- 수정 또는 완화
- 다음에 탐지하는 방법
- 후속 작업

## 관련성

해결된 실패는 project learning으로 승격할 수 있다. 단, 구체적인 failure note를 모호한 일반 규칙으로 대체하지 않는다.

## 인덱스

아직 기록된 실패가 없다.
