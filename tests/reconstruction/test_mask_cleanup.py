import numpy as np
import pytest

from object3d.reconstruction.mask_cleanup import clean_mask_for_object_prior


def test_clean_mask_largest_component_removes_disconnected_fragments() -> None:
    mask = np.zeros((8, 9), dtype=bool)
    mask[2:6, 2:7] = True
    mask[0, 0] = True
    mask[7, 8] = True

    cleaned, summary = clean_mask_for_object_prior(
        mask,
        mode="largest_component",
        erode_pixels=0,
    )

    assert cleaned.sum() == 20
    assert cleaned[2:6, 2:7].all()
    assert not cleaned[0, 0]
    assert not cleaned[7, 8]
    assert summary == {
        "mask_cleanup": "largest_component",
        "mask_erode_pixels": 0,
        "mask_pixels_before_cleanup": 22,
        "mask_pixels_after_cleanup": 20,
        "removed_mask_pixels": 2,
    }


def test_clean_mask_can_erode_noisy_boundaries() -> None:
    mask = np.ones((5, 5), dtype=bool)

    cleaned, summary = clean_mask_for_object_prior(
        mask,
        mode="none",
        erode_pixels=1,
    )

    expected = np.zeros((5, 5), dtype=bool)
    expected[1:4, 1:4] = True
    np.testing.assert_array_equal(cleaned, expected)
    assert summary["mask_pixels_before_cleanup"] == 25
    assert summary["mask_pixels_after_cleanup"] == 9
    assert summary["removed_mask_pixels"] == 16


def test_clean_mask_rejects_invalid_options() -> None:
    mask = np.ones((3, 3), dtype=bool)

    with pytest.raises(ValueError, match="mode"):
        clean_mask_for_object_prior(mask, mode="unknown", erode_pixels=0)

    with pytest.raises(ValueError, match="erode_pixels"):
        clean_mask_for_object_prior(mask, mode="none", erode_pixels=-1)
