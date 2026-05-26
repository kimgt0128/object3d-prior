"""대표 smoke fixture를 생성하는 유틸.

실제 사용자 사진은 커밋하지 않는다. 대신 실제 검증에서 안정적이었던
객체 유형을 synthetic 이미지와 prompt로 재현해 regression smoke에 쓴다.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from object3d.capture.image_io import save_png_rgb


SmokeFixtureRole = Literal["representative_success", "risk", "excluded"]

REPRESENTATIVE_SMOKE_CASE_IDS = ("laptop", "receipt", "tablet_keyboard")


@dataclass(frozen=True)
class SmokeFixtureCase:
    """실제 사진 검증 결과에서 뽑아낸 smoke/risk 케이스 정의."""

    case_id: str
    object_id: str
    label_ko: str
    role: SmokeFixtureRole
    source_observation: str
    next_action: str
    box_xyxy: tuple[int, int, int, int] | None = None
    image_size_wh: tuple[int, int] = (320, 240)
    geometry_depth_m: float = 2.0


def smoke_fixture_catalog() -> tuple[SmokeFixtureCase, ...]:
    """대표 성공/risk/excluded 케이스 catalog를 반환한다."""
    return (
        SmokeFixtureCase(
            case_id="laptop",
            object_id="laptop_001",
            label_ko="노트북",
            role="representative_success",
            source_observation="화면, 키보드, 본체를 대부분 포함해 큰 객체 대표 샘플로 적합했다.",
            next_action="대표 smoke fixture로 고정한다.",
            box_xyxy=(48, 42, 280, 206),
            geometry_depth_m=2.2,
        ),
        SmokeFixtureCase(
            case_id="receipt",
            object_id="receipt_001",
            label_ko="영수증",
            role="representative_success",
            source_observation="작은 종이 객체를 깔끔하게 분리했다.",
            next_action="작은 평면 객체 대표 smoke fixture로 고정한다.",
            box_xyxy=(126, 74, 214, 142),
            geometry_depth_m=1.3,
        ),
        SmokeFixtureCase(
            case_id="tablet_keyboard",
            object_id="tablet_keyboard_001",
            label_ko="태블릿+키보드",
            role="representative_success",
            source_observation="전체 기기 윤곽을 가장 안정적으로 분리했다.",
            next_action="경계가 큰 전자기기 대표 smoke fixture로 고정한다.",
            box_xyxy=(46, 36, 282, 218),
            geometry_depth_m=1.8,
        ),
        SmokeFixtureCase(
            case_id="transparent_cup",
            object_id="transparent_cup_001",
            label_ko="투명 컵",
            role="risk",
            source_observation="mask는 잡히지만 투명 재질 때문에 탁자/배경과 섞였다.",
            next_action="투명체 risk set으로 분리하고 실제 depth adapter 이후 재검증한다.",
        ),
        SmokeFixtureCase(
            case_id="partial_cup",
            object_id="partial_cup_001",
            label_ko="부분 컵",
            role="risk",
            source_observation="잘린 컵도 잡히지만 crop 때문에 bbox 의미가 제한됐다.",
            next_action="crop/object truncation risk set으로 분리한다.",
        ),
        SmokeFixtureCase(
            case_id="tablet_screen",
            object_id="tablet_screen_001",
            label_ko="태블릿 화면",
            role="risk",
            source_observation="화면 내부 UI와 반사 때문에 mask가 거칠어졌다.",
            next_action="초기 MVP에서는 화면 단독 대신 태블릿 전체를 대표 객체로 사용한다.",
        ),
        SmokeFixtureCase(
            case_id="straw",
            object_id="straw_001",
            label_ko="빨대",
            role="excluded",
            source_observation="얇은 물체라 주변 컵/탁자까지 같이 잡혔다.",
            next_action="일반 object prior 대상에서 제외하고 필요 시 얇은 물체 전용 후처리로 다룬다.",
        ),
        SmokeFixtureCase(
            case_id="failed_receipt_prompt",
            object_id="failed_receipt_prompt_001",
            label_ko="첫 번째 영수증 prompt",
            role="excluded",
            source_observation="prompt가 컵 주변부로 끌려가 실제 영수증 대신 다른 영역을 잡았다.",
            next_action="더 타이트한 box, negative point, prompt 재시도 정책 후보로 남긴다.",
        ),
    )


def materialize_smoke_fixtures(
    output_dir: Path,
    *,
    include_roles: tuple[SmokeFixtureRole, ...] = ("representative_success",),
) -> dict:
    """선택한 role의 synthetic smoke fixture를 디스크에 생성한다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        case
        for case in smoke_fixture_catalog()
        if case.role in include_roles and case.box_xyxy is not None
    ]
    manifest = {
        "source": "synthetic_representative_smoke_fixtures",
        "cases": [_materialize_case(case, output_dir) for case in cases],
    }
    manifest_path = output_dir / "manifest.json"
    manifest["manifest_json"] = str(manifest_path)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _materialize_case(case: SmokeFixtureCase, output_dir: Path) -> dict:
    case_dir = output_dir / case.case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    image_path = case_dir / "image.png"
    prompt_path = case_dir / "prompt.json"
    geometry_path = case_dir / "geometry.npz"
    metadata_path = case_dir / "metadata.json"

    image = _draw_case_image(case)
    save_png_rgb(image, image_path)
    _write_case_geometry_npz(case, geometry_path)
    prompt = {
        "box_xyxy": list(case.box_xyxy or (0, 0, 1, 1)),
        "multimask_output": True,
    }
    prompt_path.write_text(
        json.dumps(prompt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    metadata = asdict(case) | {
        "image_path": str(image_path),
        "prompt_json": str(prompt_path),
        "geometry_npz": str(geometry_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata | {"metadata_json": str(metadata_path)}


def _write_case_geometry_npz(case: SmokeFixtureCase, geometry_path: Path) -> None:
    width, height = case.image_size_wh
    depth_m = np.full((height, width), case.geometry_depth_m, dtype=np.float32)
    focal = float(max(width, height))
    intrinsics = np.array(
        [
            [focal, 0.0, width / 2.0],
            [0.0, focal, height / 2.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    camera_to_world = np.eye(4, dtype=np.float32)
    np.savez(
        geometry_path,
        depth_m=depth_m,
        intrinsics=intrinsics,
        camera_to_world=camera_to_world,
    )


def _draw_case_image(case: SmokeFixtureCase) -> np.ndarray:
    width, height = case.image_size_wh
    image = np.full((height, width, 3), (228, 210, 174), dtype=np.uint8)
    _draw_table_grain(image)

    if case.case_id == "laptop":
        _fill_rect(image, (54, 48, 274, 134), (42, 45, 50))
        _fill_rect(image, (66, 58, 262, 124), (95, 132, 170))
        _fill_rect(image, (48, 132, 280, 204), (70, 72, 76))
        _fill_rect(image, (96, 154, 232, 188), (45, 47, 50))
    elif case.case_id == "receipt":
        _fill_rect(image, (126, 74, 214, 142), (246, 244, 238))
        _fill_rect(image, (136, 88, 204, 94), (190, 190, 185))
        _fill_rect(image, (136, 104, 198, 110), (190, 190, 185))
        _fill_rect(image, (136, 120, 188, 126), (190, 190, 185))
    elif case.case_id == "tablet_keyboard":
        _fill_rect(image, (62, 40, 266, 132), (36, 40, 48))
        _fill_rect(image, (74, 52, 254, 122), (82, 118, 164))
        _fill_rect(image, (46, 132, 282, 218), (58, 58, 60))
        for row in range(6):
            for col in range(10):
                x0 = 64 + col * 20
                y0 = 146 + row * 10
                _fill_rect(image, (x0, y0, x0 + 14, y0 + 6), (26, 26, 28))
    else:
        if case.box_xyxy is not None:
            _fill_rect(image, case.box_xyxy, (96, 128, 180))
    return image


def _draw_table_grain(image: np.ndarray) -> None:
    for x_coord in range(0, image.shape[1], 18):
        color = 205 + (x_coord % 36)
        image[:, x_coord : x_coord + 2, :] = np.array((color, 190, 145), dtype=np.uint8)


def _fill_rect(
    image: np.ndarray,
    box_xyxy: tuple[int, int, int, int],
    color_rgb: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box_xyxy
    image[y0:y1, x0:x1, :] = np.array(color_rgb, dtype=np.uint8)
