"""manifest write/read 라운드트립 테스트."""

import json

from object3d.capture.manifest import build_manifest, read_manifest, write_manifest
from object3d.capture.records import CaptureMetadata, FrameRecord


def _sample_metadata():
    return CaptureMetadata(
        object_name="cardboard_box",
        measured_cm={"width": 30.0, "depth": 20.0, "height": 15.0},
        camera_mode="handheld",
        lighting="indoor_diffuse",
        material="cardboard",
        source_video="data/raw/box.mp4",
        source_fps=30.0,
    )


def _sample_frames():
    return [
        FrameRecord(
            frame_id=0,
            image_path="frames/frame_000000.png",
            timestamp_s=0.0,
            camera_metadata={"source_index": 0},
        ),
        FrameRecord(
            frame_id=1,
            image_path="frames/frame_000001.png",
            timestamp_s=0.2,
            camera_metadata={"source_index": 6},
        ),
    ]


def test_build_manifest_structure():
    manifest = build_manifest(_sample_metadata(), _sample_frames())
    assert manifest["schema_version"] == 1
    assert "capture_metadata" in manifest
    assert len(manifest["frames"]) == 2
    assert manifest["frames"][0]["frame_id"] == 0


def test_manifest_write_read_round_trip(tmp_path):
    manifest = build_manifest(_sample_metadata(), _sample_frames())
    path = tmp_path / "manifest.json"
    write_manifest(manifest, path)

    assert path.exists()
    loaded = read_manifest(path)
    assert loaded == manifest


def test_manifest_file_is_valid_json(tmp_path):
    manifest = build_manifest(_sample_metadata(), _sample_frames())
    path = tmp_path / "manifest.json"
    write_manifest(manifest, path)

    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    assert raw["schema_version"] == 1
    assert raw["capture_metadata"]["object_name"] == "cardboard_box"
