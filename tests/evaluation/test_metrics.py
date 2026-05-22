import numpy as np
import pytest

from object3d.evaluation.metrics import dimension_errors


def test_dimension_errors_returns_absolute_and_relative_errors() -> None:
    predicted = np.array([2.0, 3.0, 4.0], dtype=np.float32)
    measured = np.array([1.0, 3.0, 2.0], dtype=np.float32)

    result = dimension_errors(predicted, measured)

    assert result["absolute_error_m"] == [1.0, 0.0, 2.0]
    assert result["relative_error_percent"] == [100.0, 0.0, 100.0]


def test_dimension_errors_rejects_zero_measured_dimension() -> None:
    with pytest.raises(ValueError, match="non-zero"):
        dimension_errors(
            np.array([1.0, 1.0, 1.0], dtype=np.float32),
            np.array([1.0, 0.0, 1.0], dtype=np.float32),
        )
