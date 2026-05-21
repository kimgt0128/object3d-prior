"""프레임 샘플링 인덱스 계산.

순수 함수만 둔다. 영상 I/O나 파일 저장과 분리해 단위 테스트가 쉽게 한다.
"""

from __future__ import annotations

from typing import List


def compute_sample_indices(
    total_frames: int,
    source_fps: float,
    target_fps: float,
) -> List[int]:
    """원본 프레임 중 유지할 인덱스 목록을 계산한다.

    원본 fps를 target fps로 다운샘플링한다. 정수 step은
    ``floor(source_fps / target_fps)`` 로 정한다. target_fps가
    source_fps 이상이면 업샘플링하지 않고 모든 프레임을 유지한다.

    Args:
        total_frames: 원본 영상의 전체 프레임 수.
        source_fps: 원본 영상의 초당 프레임 수.
        target_fps: 원하는 초당 프레임 수.

    Returns:
        유지할 원본 프레임 인덱스의 오름차순 리스트.

    Raises:
        ValueError: fps가 양수가 아니거나 total_frames가 음수일 때.
    """
    if source_fps <= 0:
        raise ValueError(f"source_fps must be positive, got {source_fps}")
    if target_fps <= 0:
        raise ValueError(f"target_fps must be positive, got {target_fps}")
    if total_frames < 0:
        raise ValueError(f"total_frames must be non-negative, got {total_frames}")

    if total_frames == 0:
        return []

    # target이 source 이상이면 업샘플링하지 않고 전 프레임 유지.
    if target_fps >= source_fps:
        return list(range(total_frames))

    step = int(source_fps // target_fps)
    if step < 1:
        step = 1
    return list(range(0, total_frames, step))
