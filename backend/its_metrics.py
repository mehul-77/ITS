import numpy as np


def road_density(binary_mask: np.ndarray) -> float:
    road_pixels = int(np.count_nonzero(binary_mask > 0))
    total_pixels = binary_mask.size
    if total_pixels == 0:
        return 0.0
    return road_pixels / total_pixels


def road_length_estimate(skeleton_uint8: np.ndarray) -> int:
    """
    Approximate road length as number of skeleton pixels.
    Returns integer count of skeleton pixels.
    """
    return int(np.count_nonzero(skeleton_uint8 > 0))


def compute_all_metrics(binary_mask: np.ndarray, skeleton_uint8: np.ndarray, intersection_count: int) -> dict:
    density = road_density(binary_mask)
    length = road_length_estimate(skeleton_uint8)
    return {
        "road_density": float(round(density, 6)),
        "road_length": int(length),
        "intersection_count": int(intersection_count),
    }
