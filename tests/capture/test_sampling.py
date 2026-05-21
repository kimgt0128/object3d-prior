"""compute_sample_indices 단위 테스트."""

import pytest

from object3d.capture.sampling import compute_sample_indices


def test_downsample_half_rate():
    # 30fps 영상에서 15fps로 샘플링 -> 짝수 인덱스만
    indices = compute_sample_indices(total_frames=10, source_fps=30.0, target_fps=15.0)
    assert indices == [0, 2, 4, 6, 8]


def test_downsample_third_rate():
    # 30fps -> 10fps -> 3프레임마다 하나
    indices = compute_sample_indices(total_frames=12, source_fps=30.0, target_fps=10.0)
    assert indices == [0, 3, 6, 9]


def test_target_fps_equal_to_source():
    # target == source 이면 모든 프레임을 유지
    indices = compute_sample_indices(total_frames=5, source_fps=30.0, target_fps=30.0)
    assert indices == [0, 1, 2, 3, 4]


def test_target_fps_greater_than_source():
    # target > source 이면 업샘플링하지 않고 모든 프레임만 유지
    indices = compute_sample_indices(total_frames=5, source_fps=24.0, target_fps=60.0)
    assert indices == [0, 1, 2, 3, 4]


def test_zero_frames_returns_empty():
    assert compute_sample_indices(total_frames=0, source_fps=30.0, target_fps=10.0) == []


def test_non_integer_ratio_uses_floor_spacing():
    # 24fps -> 10fps, step = floor(24/10) = 2
    indices = compute_sample_indices(total_frames=10, source_fps=24.0, target_fps=10.0)
    assert indices == [0, 2, 4, 6, 8]


def test_invalid_source_fps_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=10, source_fps=0.0, target_fps=10.0)


def test_invalid_target_fps_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=10, source_fps=30.0, target_fps=0.0)


def test_negative_total_frames_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=-1, source_fps=30.0, target_fps=10.0)
