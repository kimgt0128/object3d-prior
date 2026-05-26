import json
from pathlib import Path

import numpy as np
import pytest

from object3d.pipeline.run_manual_segmentation import run_manual_segmentation
from object3d.pipeline.run_prior_from_mask import run_prior_from_mask
from object3d.validation.smoke_fixtures import (
    REPRESENTATIVE_SMOKE_CASE_IDS,
    materialize_smoke_fixtures,
    smoke_fixture_catalog,
)


def test_smoke_fixture_catalog_separates_success_risk_and_excluded_cases() -> None:
    catalog = smoke_fixture_catalog()

    assert REPRESENTATIVE_SMOKE_CASE_IDS == (
        "laptop",
        "receipt",
        "tablet_keyboard",
    )
    assert [case.case_id for case in catalog if case.role == "representative_success"] == list(
        REPRESENTATIVE_SMOKE_CASE_IDS
    )
    assert {case.case_id for case in catalog if case.role == "risk"} == {
        "transparent_cup",
        "partial_cup",
        "tablet_screen",
    }
    assert {case.case_id for case in catalog if case.role == "excluded"} == {
        "straw",
        "failed_receipt_prompt",
    }


def test_materialize_smoke_fixtures_writes_only_representative_cases_by_default(
    tmp_path: Path,
) -> None:
    manifest = materialize_smoke_fixtures(tmp_path)

    assert [case["case_id"] for case in manifest["cases"]] == list(
        REPRESENTATIVE_SMOKE_CASE_IDS
    )
    assert manifest["source"] == "synthetic_representative_smoke_fixtures"
    for case in manifest["cases"]:
        image_path = Path(case["image_path"])
        prompt_path = Path(case["prompt_json"])
        metadata_path = Path(case["metadata_json"])
        geometry_path = Path(case["geometry_npz"])
        assert image_path.exists()
        assert prompt_path.exists()
        assert metadata_path.exists()
        assert geometry_path.exists()
        assert "/Users/" not in json.dumps(case)
        assert json.loads(prompt_path.read_text(encoding="utf-8"))["box_xyxy"]


@pytest.mark.parametrize("case_id", REPRESENTATIVE_SMOKE_CASE_IDS)
def test_representative_fixture_runs_through_manual_segmentation_and_prior(
    tmp_path: Path,
    case_id: str,
) -> None:
    manifest = materialize_smoke_fixtures(tmp_path / "fixtures")
    case = next(item for item in manifest["cases"] if item["case_id"] == case_id)

    segmentation = run_manual_segmentation(
        image_path=Path(case["image_path"]),
        prompt_json_path=Path(case["prompt_json"]),
        output_dir=tmp_path / "segmentation" / case_id,
        object_id=case["object_id"],
        frame_id=0,
        backend="manual",
    )
    prior = run_prior_from_mask(
        segmentation_summary_path=Path(segmentation["summary_json"]),
        output_dir=tmp_path / "prior" / case_id,
        depth_m=2.0,
    )

    assert segmentation["mask_pixels"] > 0
    assert prior["object_id"] == case["object_id"]
    assert prior["point_count"] == segmentation["mask_pixels"]
    assert Path(prior["point_cloud_ply"]).exists()
    assert Path(prior["bbox_ply"]).exists()


@pytest.mark.parametrize("case_id", REPRESENTATIVE_SMOKE_CASE_IDS)
def test_representative_fixture_runs_through_file_geometry_prior(
    tmp_path: Path,
    case_id: str,
) -> None:
    manifest = materialize_smoke_fixtures(tmp_path / "fixtures")
    case = next(item for item in manifest["cases"] if item["case_id"] == case_id)
    geometry_npz = Path(case["geometry_npz"])

    segmentation = run_manual_segmentation(
        image_path=Path(case["image_path"]),
        prompt_json_path=Path(case["prompt_json"]),
        output_dir=tmp_path / "segmentation" / case_id,
        object_id=case["object_id"],
        frame_id=0,
        backend="manual",
    )
    prior = run_prior_from_mask(
        segmentation_summary_path=Path(segmentation["summary_json"]),
        output_dir=tmp_path / "prior" / case_id,
        depth_m=2.0,
        geometry_npz_path=geometry_npz,
    )

    with np.load(geometry_npz) as geometry:
        expected_depth = float(geometry["depth_m"][0, 0])

    assert prior["geometry_source"] == "npz"
    assert prior["geometry_npz"] == str(geometry_npz)
    assert prior["object_id"] == case["object_id"]
    assert prior["point_count"] == segmentation["mask_pixels"]
    assert prior["center_xyz"][2] == expected_depth
    assert Path(prior["scene_manifest_json"]).exists()
