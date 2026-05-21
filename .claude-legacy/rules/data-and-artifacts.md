# 데이터와 산출물 규칙

이 파일은 입력 데이터, 중간 산출물, 실험 결과, 모델 파일을 어디에 두고 무엇을 git에 올리지 않을지 정한다.

## 저장 위치

- raw input: `data/raw/`
- generated intermediate: `data/interim/`
- processed output: `data/processed/`
- final result, report image, visualization: `data/results/`
- task-specific small artifact: `.claude/tasks/<task-name>/artifacts/`
- failure note: `.claude/failures/`

## Git에 올리지 말 것

- raw video
- 큰 dataset 원본
- model checkpoint
- downloaded model weight
- cache
- secret 또는 `.env`
- 큰 point cloud, mesh, numpy dump
- 실험 run output 전체

## 실험 기록 필수 항목

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

## Artifact index 규칙

긴 출력 대신 index를 남긴다.

```text
읽은 파일:
변경 파일:
결정:
실행 명령:
관찰 오류:
저장 출력:
다음 담당:
반복 금지:
```

## 멈출 조건

- raw dataset이나 checkpoint를 commit하려 한다.
- 실험 parameter 없이 결과만 저장하려 한다.
- screenshot 또는 visualization path 없이 시각 결과를 주장하려 한다.
- task artifact가 아닌 chat history만 상태 저장소로 쓰려 한다.
