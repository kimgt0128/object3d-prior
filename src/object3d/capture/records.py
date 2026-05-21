"""capture 단계의 데이터 스키마.

다운스트림 segmentation/geometry 단계가 재현 가능하게 소비할 수 있도록
프레임 레코드와 캡처 메타데이터를 작고 명시적인 dataclass로 정의한다.
복잡한 class hierarchy 대신 dict 라운드트립으로 JSON 직렬화한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class FrameRecord:
    """샘플링된 단일 프레임의 매니페스트 레코드.

    Attributes:
        frame_id: 샘플링 결과 내에서의 0부터 시작하는 연속 인덱스.
        image_path: 저장된 프레임 이미지 경로 (매니페스트 기준 상대 경로 권장).
        timestamp_s: 원본 영상 기준 타임스탬프(초).
        camera_metadata: 원본 인덱스 등 임의의 카메라 부가 정보.
    """

    frame_id: int
    image_path: str
    timestamp_s: float
    camera_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "image_path": self.image_path,
            "timestamp_s": self.timestamp_s,
            "camera_metadata": dict(self.camera_metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FrameRecord":
        return cls(
            frame_id=int(data["frame_id"]),
            image_path=str(data["image_path"]),
            timestamp_s=float(data["timestamp_s"]),
            camera_metadata=dict(data.get("camera_metadata", {})),
        )


@dataclass
class CaptureMetadata:
    """캡처 세션 전체에 대한 메타데이터.

    측정값(measured_cm)은 width/depth/height(cm)를 담는다. 정확도 주장은
    이 수동 실측값과 비교할 수 있을 때만 가능하므로 메타데이터로 보존한다.
    """

    object_name: str
    measured_cm: Dict[str, float]
    camera_mode: str
    lighting: str
    material: str
    source_video: str
    source_fps: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_name": self.object_name,
            "measured_cm": {k: float(v) for k, v in self.measured_cm.items()},
            "camera_mode": self.camera_mode,
            "lighting": self.lighting,
            "material": self.material,
            "source_video": self.source_video,
            "source_fps": self.source_fps,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptureMetadata":
        return cls(
            object_name=str(data["object_name"]),
            measured_cm={k: float(v) for k, v in dict(data["measured_cm"]).items()},
            camera_mode=str(data["camera_mode"]),
            lighting=str(data["lighting"]),
            material=str(data["material"]),
            source_video=str(data["source_video"]),
            source_fps=float(data["source_fps"]),
        )
