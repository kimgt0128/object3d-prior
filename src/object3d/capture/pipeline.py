"""capture 파이프라인: 소스 -> 샘플 인덱스 -> 프레임 저장 -> 매니페스트.

config-driven 실행은 후속 작업으로 미루고, 여기서는 명시적 인자를 받는
``run_capture`` 한 함수만 둔다. 다운스트림 stage가 재현 가능하게 소비할
프레임 매니페스트를 만드는 것이 목표다.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from object3d.capture.frame_source import FrameSource
from object3d.capture.image_io import save_png_rgb
from object3d.capture.manifest import build_manifest, write_manifest
from object3d.capture.records import CaptureMetadata, FrameRecord
from object3d.capture.sampling import compute_sample_indices

# 저장 파일명 규칙 (frame_id 기준 zero-padded).
_FRAME_NAME = "frame_{frame_id:06d}.png"


def run_capture(
    source: FrameSource,
    metadata: CaptureMetadata,
    target_fps: float,
    output_dir: os.PathLike | str,
    manifest_path: os.PathLike | str,
) -> Dict[str, Any]:
    """프레임을 샘플링해 이미지 파일과 매니페스트를 만든다.

    Args:
        source: 원본 프레임을 yield하는 FrameSource 구현체.
        metadata: 캡처 세션 메타데이터.
        target_fps: 원하는 초당 프레임 수.
        output_dir: 샘플링된 프레임 이미지를 저장할 디렉터리.
        manifest_path: 매니페스트 JSON을 저장할 경로.

    Returns:
        디스크에 기록한 것과 동일한 매니페스트 dict.

    Note:
        ``FrameRecord.image_path``는 매니페스트 파일 위치 기준 상대 경로로
        기록한다. 따라서 출력 디렉터리가 달라도 같은 입력이면 동일한
        매니페스트가 나와 재현성이 보장된다.
    """
    output_dir = os.fspath(output_dir)
    manifest_path = os.fspath(manifest_path)
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))

    total_frames = len(source)
    keep = set(
        compute_sample_indices(
            total_frames=total_frames,
            source_fps=source.source_fps,
            target_fps=target_fps,
        )
    )

    os.makedirs(output_dir, exist_ok=True)

    records = []
    frame_id = 0
    for src_index, timestamp_s, frame in source.iter_frames():
        if src_index not in keep:
            continue

        file_name = _FRAME_NAME.format(frame_id=frame_id)
        abs_path = os.path.join(output_dir, file_name)
        save_png_rgb(frame, abs_path)

        # 매니페스트에는 매니페스트 디렉터리 기준 상대 경로를 기록한다.
        rel_path = os.path.relpath(abs_path, manifest_dir)

        records.append(
            FrameRecord(
                frame_id=frame_id,
                image_path=rel_path,
                timestamp_s=timestamp_s,
                camera_metadata={"source_index": src_index},
            )
        )
        frame_id += 1

    manifest = build_manifest(metadata, records)
    write_manifest(manifest, manifest_path)
    return manifest
