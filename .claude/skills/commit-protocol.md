# Commit Protocol 스킬

## 목적

검증된 하나의 coherent slice만 커밋해 git history를 리뷰하기 쉽게 유지한다.

## 사용할 때

agent가 기능, 버그 수정, 문서 갱신, 실험 harness, failure note 같은 하나의 작업 단위를 끝냈을 때 사용한다.

## 사용하지 않을 때

- 검증이 끝나지 않았다.
- working tree에 unrelated change가 섞여 있다.
- 사용자가 커밋하지 말라고 했다.

## 절차

1. 변경 파일을 확인한다.
2. 논리적 관심사별로 변경을 묶는다.
3. raw video, checkpoint, cache, secret, unrelated generated file을 제외한다.
4. 관련 검증을 실행한다.
   - unit test
   - smoke test
   - visual check
   - metric comparison
5. 반복 문제를 해결했거나 새로 발견했다면 failure note를 작성하거나 갱신한다.
6. `rules/ref/commit-pr-format.md`의 한글 conventional 형식으로 커밋한다.

## 메시지 템플릿

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

## 예시

```text
feat(#3): 세션 시간 조정
fix(#8): 좌표계 변환 오류 수정
docs(#11): 리뷰 계층 문서 정리
docs(#14): 깊이 스케일 불일치 실패 기록
```

## 출력

```text
커밋 범위:
포함 파일:
제외 파일:
검증:
메시지:
다음 branch 작업:
```
