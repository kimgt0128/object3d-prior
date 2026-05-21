# 세부 리뷰 관점

[rules/ref/review-stack.md](review-stack.md)가 domain review를 요구할 때만 이 파일을 연다.

## Segmentation 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- frame 전체에서 object ID 안정성이 확인됨
- mask overlay가 시각적으로 검토됨
- confidence 또는 mask area 이상치가 기록됨
- raw mask와 filtered mask가 분리 저장됨
- prompt type이 기록됨

수정 요청 또는 반려 조건:

- mask가 floor나 wall을 객체 일부로 포함한다.
- object ID가 video 중간에 바뀐다.
- frame filtering이 너무 많은 데이터를 조용히 버린다.
- visual overlay가 없다.

## Geometry 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- camera intrinsics가 문서화됨
- depth scale convention이 문서화됨
- pose convention이 문서화됨
- fusion 전에 1프레임 point cloud가 시각화됨
- multi-frame fusion 전에 2프레임 fusion이 확인됨

수정 요청 또는 반려 조건:

- coordinate transform이 불명확하다.
- COLMAP과 learned geometry를 alignment 없이 비교한다.
- metric unit을 근거 없이 보고한다.
- back-projection을 단순 known case로 테스트할 수 없다.

## Reconstruction 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- object cloud export 전에 object mask가 적용됨
- point cloud filtering parameter가 log에 남음
- object cloud가 배경과 시각적으로 분리됨
- source frame과 mask provenance가 보존됨

수정 요청 또는 반려 조건:

- object cloud 검증 전에 full-room fusion을 시도한다.
- outlier removal 설정이 기록되지 않았다.
- 명시적 이유 없이 object ID를 합친다.

## Object Prior 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- axis convention이 문서화됨
- axis-aligned box와 oriented box가 구분됨
- 치수가 단위와 함께 보고됨
- confidence score가 데이터 품질을 반영함
- accuracy를 주장할 경우 수동 실측값 비교가 있음

수정 요청 또는 반려 조건:

- 한쪽 면만 관측한 sparse view에서 과도하게 높은 confidence를 낸다.
- width/depth/height가 바뀌었거나 설명되지 않았다.
- placement feasibility에 clearance와 uncertainty가 없다.

## Evaluation 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- 수동 ground truth가 기록됨
- 절대 오차와 상대 오차가 보고됨
- 실패 사례가 포함됨
- ablation이 실제 pipeline 선택과 연결됨

수정 요청 또는 반려 조건:

- plot이 장식용이다.
- metric이 명백한 실패 사례를 숨긴다.
- method comparison이 서로 다른 입력 조건으로 수행된다.

## Visualization 관점

아래 항목이 확인되기 전에는 승인하지 않는다.

- raw frame과 mask overlay가 보임
- camera trajectory와 object cloud가 보임
- 3D bounding box와 치수가 보임
- warning 또는 confidence가 보임

수정 요청 또는 반려 조건:

- demo가 model output만 보여주고 object prior를 보여주지 않는다.
- undocumented manual file edit이 있어야 visualization이 동작한다.
