"""object3d.capture — 입력 영상 프레임 샘플링과 캡처 메타데이터.

T1 단계의 공개 API. 다운스트림 segmentation/geometry 단계가 재현 가능하게
소비할 프레임 매니페스트를 만든다.

``src/object3d/`` 자체에는 __init__.py가 없다(PEP 420 implicit namespace
package). 실제 패키지는 ``object3d.capture`` 하나뿐이다.
"""

from object3d.capture.frame_source import (
    ArrayFrameSource,
    FrameSource,
    VideoFrameSource,
)
from object3d.capture.manifest import (
    SCHEMA_VERSION,
    build_manifest,
    read_manifest,
    write_manifest,
)
from object3d.capture.pipeline import run_capture
from object3d.capture.records import CaptureMetadata, FrameRecord
from object3d.capture.sampling import compute_sample_indices

__all__ = [
    "ArrayFrameSource",
    "FrameSource",
    "VideoFrameSource",
    "SCHEMA_VERSION",
    "build_manifest",
    "read_manifest",
    "write_manifest",
    "run_capture",
    "CaptureMetadata",
    "FrameRecord",
    "compute_sample_indices",
]
