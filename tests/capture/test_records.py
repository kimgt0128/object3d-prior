"""FrameRecord / CaptureMetadata dict 라운드트립 테스트."""

from object3d.capture.records import CaptureMetadata, FrameRecord


def test_frame_record_round_trip():
    record = FrameRecord(
        frame_id=3,
        image_path="frames/frame_000003.png",
        timestamp_s=0.1,
        camera_metadata={"source_index": 9, "exposure": "auto"},
    )
    restored = FrameRecord.from_dict(record.to_dict())
    assert restored == record


def test_capture_metadata_round_trip():
    meta = CaptureMetadata(
        object_name="cardboard_box",
        measured_cm={"width": 30.0, "depth": 20.0, "height": 15.0},
        camera_mode="handheld",
        lighting="indoor_diffuse",
        material="cardboard",
        source_video="data/raw/box.mp4",
        source_fps=30.0,
    )
    restored = CaptureMetadata.from_dict(meta.to_dict())
    assert restored == meta


def test_frame_record_to_dict_keys():
    record = FrameRecord(
        frame_id=0,
        image_path="frames/frame_000000.png",
        timestamp_s=0.0,
        camera_metadata={},
    )
    d = record.to_dict()
    assert set(d.keys()) == {
        "frame_id",
        "image_path",
        "timestamp_s",
        "camera_metadata",
    }


def test_capture_metadata_to_dict_keys():
    meta = CaptureMetadata(
        object_name="book",
        measured_cm={"width": 21.0, "depth": 3.0, "height": 29.7},
        camera_mode="tripod",
        lighting="studio",
        material="paper",
        source_video="data/raw/book.mp4",
        source_fps=24.0,
    )
    d = meta.to_dict()
    assert set(d.keys()) == {
        "object_name",
        "measured_cm",
        "camera_mode",
        "lighting",
        "material",
        "source_video",
        "source_fps",
    }
