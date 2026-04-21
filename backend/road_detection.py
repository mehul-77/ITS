import warnings

import cv2
import numpy as np
from skimage.filters import frangi


def _normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def _make_line_kernel(size: int, angle: int, thickness: int = 3) -> np.ndarray:
    kernel = np.zeros((size, size), dtype=np.uint8)
    center = size // 2
    cv2.line(kernel, (center, 1), (center, size - 2), 1, thickness)
    matrix = cv2.getRotationMatrix2D((center, center), angle, 1.0)
    rotated = cv2.warpAffine(kernel, matrix, (size, size))
    return (rotated > 0).astype(np.uint8)


def _multi_orientation_response(gray: np.ndarray, operation: int, size: int = 17) -> np.ndarray:
    response = np.zeros_like(gray)
    for angle in (0, 45, 90, 135):
        kernel = _make_line_kernel(size=size, angle=angle)
        response = np.maximum(response, cv2.morphologyEx(gray, operation, kernel))
    return response


def _percentile_mask(image: np.ndarray, percentile: float) -> np.ndarray:
    values = image[image > 0]
    if values.size == 0:
        return np.zeros_like(image)
    threshold = np.percentile(values, percentile)
    return np.where(image >= threshold, 255, 0).astype(np.uint8)


def detect_roads(img_bgr: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Conservative road extraction tuned to avoid flooding the scene.

    A pixel is kept only when there is strong evidence of elongated road structure
    plus support from road-surface or edge information.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    enhanced = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

    dark_linear = _multi_orientation_response(blurred, cv2.MORPH_BLACKHAT, size=17)
    bright_linear = _multi_orientation_response(blurred, cv2.MORPH_TOPHAT, size=15)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dark_ridges = frangi(255 - blurred, sigmas=(1, 3), black_ridges=False)
        bright_ridges = frangi(blurred, sigmas=(1, 3), black_ridges=False)

    dark_ridges_u8 = _normalize_to_uint8(dark_ridges)
    bright_ridges_u8 = _normalize_to_uint8(bright_ridges)

    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    hue = hsv[:, :, 0]

    low_saturation = np.where(saturation <= np.percentile(saturation, 48), 255, 0).astype(np.uint8)
    mid_tone = np.where(
        (value >= np.percentile(value, 18)) & (value <= np.percentile(value, 72)),
        255,
        0,
    ).astype(np.uint8)
    non_vegetation = np.where(~(((hue >= 25) & (hue <= 95)) & (saturation > np.percentile(saturation, 62))), 255, 0).astype(np.uint8)
    surface_support = cv2.bitwise_and(cv2.bitwise_and(low_saturation, mid_tone), non_vegetation)

    edges = cv2.Canny(blurred, 70, 150)
    edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    line_support = np.zeros_like(gray)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=24, minLineLength=24, maxLineGap=18)
    if lines is not None:
        for line in lines[:, 0]:
            x1, y1, x2, y2 = line
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            if length >= 35:
                cv2.line(line_support, (x1, y1), (x2, y2), 255, 7)

    dark_linear_mask = _percentile_mask(dark_linear, 80)
    bright_linear_mask = _percentile_mask(bright_linear, 88)
    dark_ridge_mask = _percentile_mask(dark_ridges_u8, 84)
    bright_ridge_mask = _percentile_mask(bright_ridges_u8, 90)

    linear_evidence = cv2.bitwise_or(
        cv2.bitwise_or(dark_linear_mask, dark_ridge_mask),
        cv2.bitwise_or(bright_linear_mask, bright_ridge_mask),
    )

    support_mask = np.zeros_like(gray, dtype=np.uint8)
    support_mask[surface_support > 0] += 1
    support_mask[edges > 0] += 1
    support_mask[line_support > 0] += 1

    road_mask = np.where((linear_evidence > 0) & (support_mask >= 1), 255, 0).astype(np.uint8)
    strong_dark = cv2.bitwise_and(dark_linear_mask, dark_ridge_mask)
    road_mask = cv2.bitwise_or(road_mask, strong_dark)
    road_mask = cv2.bitwise_or(road_mask, cv2.bitwise_and(line_support, surface_support))
    road_mask = cv2.erode(road_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)
    road_mask = cv2.dilate(road_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    road_mask = cv2.morphologyEx(
        road_mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=1,
    )
    road_mask = cv2.morphologyEx(
        road_mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
        iterations=1,
    )

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(road_mask, connectivity=8)
    final_mask = np.zeros_like(road_mask)
    min_area = max(48, int(img_bgr.shape[0] * img_bgr.shape[1] * 0.00006))
    components_kept = 0

    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        width = int(stats[idx, cv2.CC_STAT_WIDTH])
        height = int(stats[idx, cv2.CC_STAT_HEIGHT])
        aspect = max(width, height) / max(1, min(width, height))
        fill_ratio = area / max(1, width * height)

        if area >= min_area and ((aspect >= 2.0 and fill_ratio <= 0.62) or area >= min_area * 12):
            final_mask[labels == idx] = 255
            components_kept += 1

    metadata = {
        "method": "advanced_linear_structure_with_line_support",
        "components_kept": components_kept,
        "min_component_area_px": min_area,
        "hough_lines": 0 if lines is None else int(len(lines)),
    }
    return final_mask, metadata
