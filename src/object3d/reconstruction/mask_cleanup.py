"""Mask cleanup utilities before lifting segmentation into 3D."""

from __future__ import annotations

from typing import Any

import numpy as np


MASK_CLEANUP_MODES = ("none", "largest_component")


def clean_mask_for_object_prior(
    mask: np.ndarray,
    *,
    mode: str = "none",
    erode_pixels: int = 0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Prepare a binary object mask for 3D backprojection."""
    if mode not in MASK_CLEANUP_MODES:
        raise ValueError("mode must be 'none' or 'largest_component'")
    if erode_pixels < 0:
        raise ValueError("erode_pixels must be greater than or equal to 0")

    mask_bool = np.asarray(mask, dtype=bool)
    if mask_bool.ndim != 2:
        raise ValueError("mask must be a 2D array")

    before_count = int(mask_bool.sum())
    cleaned = mask_bool.copy()
    if mode == "largest_component":
        cleaned = _largest_connected_component(cleaned)
    if erode_pixels:
        cleaned = _erode_mask(cleaned, pixels=erode_pixels)

    after_count = int(cleaned.sum())
    if before_count > 0 and after_count == 0:
        raise ValueError("mask cleanup produced an empty mask")

    return cleaned, {
        "mask_cleanup": mode,
        "mask_erode_pixels": int(erode_pixels),
        "mask_pixels_before_cleanup": before_count,
        "mask_pixels_after_cleanup": after_count,
        "removed_mask_pixels": int(before_count - after_count),
    }


def _largest_connected_component(mask: np.ndarray) -> np.ndarray:
    if not np.any(mask):
        return mask.copy()

    try:
        return _largest_connected_component_cv2(mask)
    except Exception:
        return _largest_connected_component_numpy(mask)


def _largest_connected_component_cv2(mask: np.ndarray) -> np.ndarray:
    import cv2

    label_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8),
        connectivity=8,
    )
    if label_count <= 1:
        return mask.copy()

    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = int(np.argmax(areas)) + 1
    return np.asarray(labels == largest_label, dtype=bool)


def _largest_connected_component_numpy(mask: np.ndarray) -> np.ndarray:
    visited = np.zeros(mask.shape, dtype=bool)
    best_component: list[tuple[int, int]] = []
    height, width = mask.shape

    ys, xs = np.nonzero(mask)
    for start_y, start_x in zip(ys.tolist(), xs.tolist(), strict=True):
        if visited[start_y, start_x]:
            continue

        component: list[tuple[int, int]] = []
        stack = [(start_y, start_x)]
        visited[start_y, start_x] = True
        while stack:
            y, x = stack.pop()
            component.append((y, x))
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if visited[ny, nx] or not mask[ny, nx]:
                        continue
                    visited[ny, nx] = True
                    stack.append((ny, nx))

        if len(component) > len(best_component):
            best_component = component

    cleaned = np.zeros(mask.shape, dtype=bool)
    if best_component:
        component_y, component_x = zip(*best_component, strict=True)
        cleaned[np.asarray(component_y), np.asarray(component_x)] = True
    return cleaned


def _erode_mask(mask: np.ndarray, *, pixels: int) -> np.ndarray:
    try:
        return _erode_mask_cv2(mask, pixels=pixels)
    except Exception:
        return _erode_mask_numpy(mask, pixels=pixels)


def _erode_mask_cv2(mask: np.ndarray, *, pixels: int) -> np.ndarray:
    import cv2

    kernel = np.ones((3, 3), dtype=np.uint8)
    eroded = cv2.erode(
        mask.astype(np.uint8),
        kernel,
        iterations=int(pixels),
        borderType=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    return np.asarray(eroded > 0, dtype=bool)


def _erode_mask_numpy(mask: np.ndarray, *, pixels: int) -> np.ndarray:
    eroded = mask.copy()
    for _ in range(pixels):
        height, width = eroded.shape
        padded = np.pad(eroded, 1, mode="constant", constant_values=False)
        neighborhoods = [
            padded[y_offset : y_offset + height, x_offset : x_offset + width]
            for y_offset in range(3)
            for x_offset in range(3)
        ]
        eroded = np.logical_and.reduce(neighborhoods)
    return np.asarray(eroded, dtype=bool)
