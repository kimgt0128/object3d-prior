# Experiment Logging 스킬

## 목적

실험을 재현 가능하게 만들고 parameter search가 추적 불가능해지는 것을 막는다.

## 사용할 때

pipeline, model, threshold search, ablation을 실행할 때 사용한다.

## 사용하지 않을 때

- 실험을 실행하지 않았다.
- 문서 구조만 작성한다.
- 입력, 파라미터, metric이 없는 출력이다.

## 필수 기록 항목

- 날짜
- dataset 또는 video 이름
- object category
- model version
- prompt type
- frame sampling rate
- mask filtering threshold
- depth 또는 pose source
- point cloud filtering parameter
- bounding box method
- manual measurement
- predicted measurement
- observed failure case
- screenshot 또는 visualization path

## 절차

1. `.claude/tasks/<task-name>/artifacts/` 아래 run artifact를 만들거나 갱신한다.
2. 입력, 파라미터, model version, output path를 기록한다.
3. metric과 visual evidence path를 붙인다.
4. 반복 실패는 `.claude/failures/`에 연결한다.

## 출력

```text
run artifact 경로:
입력:
파라미터:
metric:
시각 근거:
failure note:
다음 실험:
```
