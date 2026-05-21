"""의존성 없는 PNG 저장 유틸.

프레임 이미지를 디스크에 쓸 때 cv2/Pillow 같은 추가 의존성을 요구하지
않도록, Python stdlib(zlib/struct)만으로 8-bit RGB PNG를 인코딩한다.

이 모듈은 capture 파이프라인의 결정적 저장 단계에만 쓰인다. 같은 입력
배열이면 항상 동일한 바이트열을 만들어 재현성을 보장한다.
"""

from __future__ import annotations

import os
import struct
import zlib

import numpy as np


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    """PNG 청크 한 개(length + tag + data + CRC)를 만든다."""
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png_rgb(frame: np.ndarray) -> bytes:
    """(H, W, 3) uint8 RGB 배열을 PNG 바이트열로 인코딩한다."""
    arr = np.asarray(frame)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"expected (H, W, 3) RGB frame, got shape {arr.shape}")
    if arr.dtype != np.uint8:
        # 캡처 단계 입력은 uint8을 기대한다. 다른 dtype은 명시적으로 캐스팅.
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    height, width, _ = arr.shape

    # 각 스캔라인 앞에 filter type 0(None) 바이트를 붙인다.
    filter_column = np.zeros((height, 1), dtype=np.uint8)
    rows = np.hstack([filter_column, arr.reshape(height, width * 3)])
    raw = rows.tobytes()

    signature = b"\x89PNG\r\n\x1a\n"
    # IHDR: width, height, bit depth 8, color type 2(RGB), 압축/필터/인터레이스 0
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    return (
        signature
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


def save_png_rgb(frame: np.ndarray, path: os.PathLike | str) -> None:
    """RGB 프레임 배열을 PNG 파일로 저장한다 (부모 디렉터리 자동 생성)."""
    path = os.fspath(path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(encode_png_rgb(frame))
