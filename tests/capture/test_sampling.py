"""compute_sample_indices / FrameSampler 단위 테스트."""

import math

import pytest

from object3d.capture.sampling import FrameSampler, compute_sample_indices


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


def test_non_integer_ratio_tracks_target_fps():
    """비정수 fps 비율에서도 유효 fps가 target에 수렴해야 한다 (Bug 1).

    24fps -> 10fps. 옛 정수 floor step(=floor(24/10)=2)은 유효 12fps로 20%
    overshoot한다. rational rule은 24프레임(1초) 중 target_fps(=10)±1을
    유지하고, 첫 프레임 0은 항상 포함하며 균등 간격이어야 한다.
    """
    indices = compute_sample_indices(total_frames=24, source_fps=24.0, target_fps=10.0)
    # 첫 프레임은 항상 유지.
    assert indices[0] == 0
    # 1초 동안 유지된 프레임 수가 target_fps ±1 이내.
    assert abs(len(indices) - 10) <= 1
    # 옛 floor-step 동작(짝수 12개)으로 회귀하지 않음.
    assert indices != [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    # rational rule의 결정적 결과.
    assert indices == [0, 3, 5, 8, 10, 12, 15, 17, 20, 22]


@pytest.mark.parametrize(
    "source_fps,target_fps",
    [(29.97, 10.0), (25.0, 12.0), (59.94, 15.0), (24.0, 10.0)],
)
def test_effective_fps_within_one_of_target(source_fps, target_fps):
    """1초 분량(round(source_fps) 프레임)에서 유지 수가 target ±1."""
    one_second = round(source_fps)
    indices = compute_sample_indices(
        total_frames=one_second, source_fps=source_fps, target_fps=target_fps
    )
    assert indices[0] == 0, "index 0은 항상 유지"
    assert abs(len(indices) - target_fps) <= 1, (
        f"{source_fps}->{target_fps}: 1초 동안 {len(indices)}프레임 유지, "
        f"target {target_fps}±1 벗어남"
    )


def test_2997_to_10_keeps_ten_frames():
    # 29.97fps phone video -> 10fps. 1초(30프레임)에서 정확히 10프레임.
    indices = compute_sample_indices(total_frames=30, source_fps=29.97, target_fps=10.0)
    assert len(indices) == 10
    assert indices[0] == 0


def test_25_to_12_keeps_twelve_frames():
    # 25fps -> 12fps. ceil(25/12)=2 step이면 13프레임으로 under/overshoot.
    # rational rule은 1초(25프레임)에서 정확히 12프레임.
    indices = compute_sample_indices(total_frames=25, source_fps=25.0, target_fps=12.0)
    assert len(indices) == 12
    assert indices[0] == 0


def test_indices_are_evenly_spaced():
    # rational rule은 간격이 floor/ceil step 하나로만 구성되어야 한다.
    indices = compute_sample_indices(total_frames=30, source_fps=29.97, target_fps=10.0)
    gaps = {indices[i + 1] - indices[i] for i in range(len(indices) - 1)}
    # 간격은 연속된 두 정수만 사용 (균등 분포).
    assert len(gaps) <= 2
    assert max(gaps) - min(gaps) <= 1


def test_invalid_source_fps_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=10, source_fps=0.0, target_fps=10.0)


def test_invalid_target_fps_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=10, source_fps=30.0, target_fps=0.0)


def test_negative_total_frames_raises():
    with pytest.raises(ValueError):
        compute_sample_indices(total_frames=-1, source_fps=30.0, target_fps=10.0)


# --- FrameSampler (streaming, no total count) ---


def test_frame_sampler_matches_compute_sample_indices():
    """스트리밍 sampler가 compute_sample_indices와 동일한 keep-set을 낸다."""
    sampler = FrameSampler(source_fps=29.97, target_fps=10.0)
    streamed = [i for i in range(30) if sampler.should_keep(i)]
    batch = compute_sample_indices(total_frames=30, source_fps=29.97, target_fps=10.0)
    assert streamed == batch


def test_frame_sampler_keeps_index_zero():
    sampler = FrameSampler(source_fps=29.97, target_fps=10.0)
    assert sampler.should_keep(0) is True


def test_frame_sampler_no_total_count_needed():
    """sampler는 전체 프레임 수 없이 인덱스만으로 동작한다."""
    sampler = FrameSampler(source_fps=25.0, target_fps=12.0)
    kept = sum(1 for i in range(25) if sampler.should_keep(i))
    assert kept == 12


def test_frame_sampler_upsample_keeps_all():
    sampler = FrameSampler(source_fps=24.0, target_fps=60.0)
    assert all(sampler.should_keep(i) for i in range(10))


def test_frame_sampler_invalid_fps_raises():
    with pytest.raises(ValueError):
        FrameSampler(source_fps=0.0, target_fps=10.0)
    with pytest.raises(ValueError):
        FrameSampler(source_fps=30.0, target_fps=0.0)
