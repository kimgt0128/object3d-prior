import sys
from pathlib import Path

import numpy as np
import pytest

from object3d.adapters.segmentation.sam import (
    OptionalSegmentationDependencyError,
    SamPrompt,
    load_sam_predictor,
    predict_mask,
)
from object3d.capture.records import FrameRecord


class FakePredictor:
    def __init__(self) -> None:
        self.image_shape = None
        self.received_box = None
        self.received_point_coords = None
        self.received_point_labels = None

    def set_image(self, image: np.ndarray) -> None:
        self.image_shape = image.shape

    def predict(self, **kwargs):
        self.received_box = kwargs["box"]
        self.received_point_coords = kwargs["point_coords"]
        self.received_point_labels = kwargs["point_labels"]
        first = np.zeros((6, 8), dtype=bool)
        second = np.ones((6, 8), dtype=bool)
        masks = np.stack([first, second])
        scores = np.array([0.25, 0.9], dtype=np.float32)
        return masks, scores, None


def test_sam_prompt_requires_box_or_points() -> None:
    with pytest.raises(ValueError, match="box or points"):
        SamPrompt()


def test_predict_mask_uses_injected_predictor_and_selects_best_score() -> None:
    frame = FrameRecord(frame_id=3, image_path="frame_000003.png", timestamp_s=0.3)
    image = np.zeros((6, 8, 3), dtype=np.uint8)
    predictor = FakePredictor()
    prompt = SamPrompt(
        box_xyxy=(1.0, 2.0, 7.0, 5.0),
        point_coords_xy=((4.0, 3.0),),
        point_labels=(1,),
    )

    mask = predict_mask(
        frame,
        image=image,
        object_id="chair_001",
        predictor=predictor,
        prompt=prompt,
    )

    assert predictor.image_shape == (6, 8, 3)
    np.testing.assert_allclose(predictor.received_box, np.array([1.0, 2.0, 7.0, 5.0]))
    np.testing.assert_allclose(predictor.received_point_coords, np.array([[4.0, 3.0]]))
    np.testing.assert_array_equal(predictor.received_point_labels, np.array([1]))
    assert mask.frame_id == 3
    assert mask.object_id == "chair_001"
    assert mask.confidence == pytest.approx(0.9)
    assert mask.mask.dtype == np.bool_
    assert mask.mask.shape == (6, 8)
    assert mask.mask.all()


def test_load_sam_predictor_reports_missing_optional_dependency(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "segment_anything", None)

    with pytest.raises(OptionalSegmentationDependencyError, match="segment_anything"):
        load_sam_predictor(
            backend="sam",
            checkpoint_path=Path("missing-checkpoint.pth"),
            model_type="vit_b",
        )


def test_load_sam2_predictor_reports_missing_optional_dependency(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "sam2.build_sam", None)

    with pytest.raises(OptionalSegmentationDependencyError, match="sam2"):
        load_sam_predictor(
            backend="sam2",
            checkpoint_path=Path("missing-checkpoint.pt"),
            model_type="sam2_hiera_t",
            config_path=Path("sam2_hiera_t.yaml"),
        )
