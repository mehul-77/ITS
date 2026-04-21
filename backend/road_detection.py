import cv2
import numpy as np
from skimage.morphology import skeletonize


def _vegetation_mask(img_bgr: np.ndarray, hsv: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(img_bgr.astype(np.int16))
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    excess_green = 2 * g - r - b
    return (((h >= 25) & (h <= 95) & (s > 38)) | (excess_green > 12)).astype(np.uint8) * 255


def _local_std(gray: np.ndarray, ksize: int = 15) -> np.ndarray:
    gray_f = gray.astype(np.float32)
    mean = cv2.blur(gray_f, (ksize, ksize))
    sq_mean = cv2.blur(gray_f * gray_f, (ksize, ksize))
    return np.sqrt(np.maximum(sq_mean - mean * mean, 0))


def _road_surface_candidates(img_bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    a, b = lab[:, :, 1], lab[:, :, 2]
    vegetation = _vegetation_mask(img_bgr, hsv)
    std = _local_std(gray)

    # Asphalt/concrete roads in these tiles are generally grey, not very bright,
    # non-vegetated, and smoother than dense roof blocks.
    neutral = (np.abs(a.astype(np.int16) - 128) < 14) & (np.abs(b.astype(np.int16) - 128) < 16)
    asphalt = (
        (s < 76)
        & (v > 35)
        & (v < 162)
        & neutral
        & (vegetation == 0)
        & (std < 48)
    )

    candidates = asphalt.astype(np.uint8) * 255
    candidates = cv2.morphologyEx(candidates, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)
    candidates = cv2.morphologyEx(candidates, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=1)
    return candidates


def _long_corridor_support(gray: np.ndarray, candidates: np.ndarray) -> tuple[np.ndarray, int]:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 60, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=48, minLineLength=70, maxLineGap=24)

    support = np.zeros_like(gray)
    accepted = 0
    if lines is None:
        return support, accepted

    for x1, y1, x2, y2 in lines[:, 0]:
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if length < 75:
            continue

        probe = np.zeros_like(gray)
        cv2.line(probe, (x1, y1), (x2, y2), 255, 13)
        candidate_ratio = (candidates[probe > 0] > 0).mean() if np.any(probe > 0) else 0
        if candidate_ratio >= 0.28:
            cv2.line(support, (x1, y1), (x2, y2), 255, 17)
            accepted += 1

    support = cv2.morphologyEx(support, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=1)
    return support, accepted


def detect_roads(img_bgr: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Fast detector for dense Indian urban satellite tiles.

    It prioritizes grey asphalt/concrete corridors and rejects many bright roof,
    tree, and open-ground false positives. This is intentionally lightweight so
    uploads remain responsive during demos.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    candidates = _road_surface_candidates(img_bgr)
    corridor_support, line_count = _long_corridor_support(gray, candidates)

    supported = cv2.bitwise_and(candidates, cv2.dilate(corridor_support, np.ones((5, 5), np.uint8), iterations=1))
    road_mask = cv2.bitwise_or(supported, cv2.bitwise_and(candidates, corridor_support))
    road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=2)
    road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(road_mask, connectivity=8)
    final_mask = np.zeros_like(road_mask)
    h, w = road_mask.shape
    min_area = max(80, int(h * w * 0.00018))
    kept = 0

    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        x = int(stats[idx, cv2.CC_STAT_LEFT])
        y = int(stats[idx, cv2.CC_STAT_TOP])
        cw = int(stats[idx, cv2.CC_STAT_WIDTH])
        ch = int(stats[idx, cv2.CC_STAT_HEIGHT])
        aspect = max(cw, ch) / max(1, min(cw, ch))
        touches_border = x <= 2 or y <= 2 or (x + cw) >= w - 2 or (y + ch) >= h - 2

        if area >= min_area and (aspect >= 1.35 or touches_border or area >= min_area * 6):
            final_mask[labels == idx] = 255
            kept += 1

    if np.any(final_mask):
        distance = cv2.distanceTransform((final_mask > 0).astype(np.uint8), cv2.DIST_L2, 3)
        skeleton = skeletonize(final_mask > 0)
        centerline = np.logical_and(skeleton, np.logical_and(distance >= 2.0, distance <= 22.0))
        centerline_u8 = (centerline.astype(np.uint8)) * 255

        # Rebuild roads from plausible centerlines so large paved yards/roof blocks
        # do not dominate the road mask or density metric.
        rebuilt = cv2.dilate(
            centerline_u8,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)),
            iterations=1,
        )
        final_mask = cv2.bitwise_and(rebuilt, final_mask)

    metadata = {
        "method": "fast_urban_asphalt_corridor_detector",
        "components_kept": kept,
        "min_component_area_px": min_area,
        "corridor_lines": line_count,
    }
    return final_mask, metadata
