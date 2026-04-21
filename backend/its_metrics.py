import cv2
import numpy as np


def road_density(binary_mask: np.ndarray) -> float:
    road_pixels = int(np.count_nonzero(binary_mask > 0))
    total_pixels = binary_mask.size
    return 0.0 if total_pixels == 0 else road_pixels / total_pixels


def road_length_estimate(skeleton_uint8: np.ndarray) -> int:
    return int(np.count_nonzero(skeleton_uint8 > 0))


def average_width_estimate(binary_mask: np.ndarray, skeleton_uint8: np.ndarray) -> float:
    mask = (binary_mask > 0).astype(np.uint8)
    skel = skeleton_uint8 > 0
    if not np.any(skel):
        return 0.0
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    widths = distance[skel] * 2.0
    if widths.size == 0:
        return 0.0
    return float(np.mean(widths))


def compute_all_metrics(binary_mask: np.ndarray, skeleton_uint8: np.ndarray, features: dict) -> dict:
    density = road_density(binary_mask)
    length = road_length_estimate(skeleton_uint8)
    avg_width = average_width_estimate(binary_mask, skeleton_uint8)
    intersections = int(features.get("intersection_count", 0))
    endpoints = int(features.get("endpoint_count", 0))
    connectivity = 0.0 if (intersections + endpoints) == 0 else intersections / (intersections + endpoints)

    return {
        "road_density": float(round(density, 6)),
        "road_density_percent": float(round(density * 100, 2)),
        "road_length": int(length),
        "intersection_count": intersections,
        "endpoint_count": endpoints,
        "average_width_px": float(round(avg_width, 2)),
        "connectivity_score": float(round(connectivity, 3)),
    }
