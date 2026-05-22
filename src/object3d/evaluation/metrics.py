"""Object prior 측정값 평가 지표."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def dimension_errors(
    predicted_m: NDArray[np.float32],
    measured_m: NDArray[np.float32],
) -> dict[str, list[float]]:
    """예측 크기와 실측 크기의 절대/상대 오차를 계산한다."""
    if predicted_m.shape != measured_m.shape:
        raise ValueError("predicted_m and measured_m must have the same shape")
    if np.any(measured_m == 0):
        raise ValueError("measured dimensions must be non-zero")

    absolute = np.abs(predicted_m - measured_m)
    relative = absolute / np.abs(measured_m) * 100.0
    return {
        "absolute_error_m": [float(value) for value in absolute],
        "relative_error_percent": [float(value) for value in relative],
    }
