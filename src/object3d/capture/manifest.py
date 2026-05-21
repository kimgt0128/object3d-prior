"""프레임 매니페스트 빌드 및 JSON 직렬화.

매니페스트 구조:
``{"schema_version": 1, "capture_metadata": {...}, "frames": [FrameRecord...]}``
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Sequence

from object3d.capture.records import CaptureMetadata, FrameRecord

SCHEMA_VERSION = 1


def build_manifest(
    metadata: CaptureMetadata,
    frames: Sequence[FrameRecord],
) -> Dict[str, Any]:
    """캡처 메타데이터와 프레임 레코드로 매니페스트 dict를 만든다."""
    return {
        "schema_version": SCHEMA_VERSION,
        "capture_metadata": metadata.to_dict(),
        "frames": [frame.to_dict() for frame in frames],
    }


def write_manifest(manifest: Dict[str, Any], path: os.PathLike | str) -> None:
    """매니페스트 dict를 JSON 파일로 저장한다.

    부모 디렉터리가 없으면 생성한다. 재현성을 위해 키 순서를 보존하고
    한글 등 비ASCII 문자를 그대로 기록한다.
    """
    path = os.fspath(path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def read_manifest(path: os.PathLike | str) -> Dict[str, Any]:
    """JSON 매니페스트 파일을 dict로 읽는다."""
    with open(os.fspath(path), "r", encoding="utf-8") as fh:
        return json.load(fh)
