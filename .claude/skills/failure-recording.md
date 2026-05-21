# Failure Recording 스킬

## 목적

실패와 debugging dead end를 검색 가능한 프로젝트 기억으로 바꾼다.

## 사용할 때

실험 실패, misleading model output, parameter search 제약 발견, 조사 후 bug fix가 있었을 때 사용한다.

## 사용하지 않을 때

- “실패했다” 외에 증거가 없다.
- 재사용 교훈이 없는 단순 typo다.
- 더 구체적인 기존 failure note를 갱신하면 된다.

이 스킬은 문제가 해결된 직후 맥락이 생생할 때 학습을 기록해 다음 agent가 같은 경로를 반복하지 않게 하는 것을 목표로 한다.

## failure note 위치

```text
.claude/failures/YYYY-MM-DD-short-slug.md
```

반복 가능한 engineering lesson이 되면 나중에 더 구조화된 문서로 승격할 수 있다.

## 필수 섹션

```markdown
# 짧은 실패 제목

날짜:
상태: open | mitigated | solved
영역: segmentation | geometry | reconstruction | priors | evaluation | visualization | tooling

## 증상

무엇이 관측됐는가?

## 맥락

입력 데이터, 모델 버전, 파라미터, branch, command.

## 실패한 시도

무엇을 시도했고 왜 실패했는가?

## 원인 추정

현재 가장 그럴듯한 설명.

## 수정 또는 완화

무엇을 바꿨는가?

## 다음에 탐지하는 법

metric, log, screenshot, sanity check.

## 후속 작업

다음 agent가 무엇을 해야 하는가?
```

## 흔한 실패 유형

- SAM mask drift
- mask에 배경 포함
- learned depth scale mismatch
- COLMAP scale mismatch
- pose convention 오류
- lens distortion
- sparse object point cloud
- outlier-heavy point cloud
- bounding box axis swap
- measurement error 과다
- Rerun/Open3D visualization mismatch

## 절차

1. 새 note를 만들기 전에 기존 failure note를 검색한다.
2. 가장 구체적인 note를 만들거나 갱신한다.
3. 증거, 파라미터, 다음에 피해야 할 시도를 포함한다.
4. 관련 task artifact가 있으면 연결한다.

## 출력

```text
failure note:
상태:
증거:
재사용 교훈:
다음 담당:
```
