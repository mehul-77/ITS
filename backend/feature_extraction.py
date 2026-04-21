import cv2
import numpy as np
from skimage.morphology import skeletonize


def skeletonize_mask(binary_mask: np.ndarray) -> np.ndarray:
    bw = (binary_mask > 0).astype(np.uint8)
    skel_bool = skeletonize(bw > 0)
    return (skel_bool.astype(np.uint8)) * 255


def _neighbor_counts(skeleton_uint8: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    skel = (skeleton_uint8 > 0).astype(np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)
    neighbor_sum = cv2.filter2D(skel, -1, kernel) - skel
    return skel, neighbor_sum


def _merge_close_points(points: list[tuple[int, int]], merge_radius: float = 10.0) -> list[tuple[int, int]]:
    merged = []
    remaining = points[:]

    while remaining:
        seed_x, seed_y = remaining.pop(0)
        group = [(seed_x, seed_y)]
        leftovers = []

        for px, py in remaining:
            if ((px - seed_x) ** 2 + (py - seed_y) ** 2) ** 0.5 <= merge_radius:
                group.append((px, py))
            else:
                leftovers.append((px, py))

        avg_x = int(round(sum(p[0] for p in group) / len(group)))
        avg_y = int(round(sum(p[1] for p in group) / len(group)))
        merged.append((avg_x, avg_y))
        remaining = leftovers

    return merged


def _extract_cluster_centers(mask: np.ndarray, min_area: int = 3, merge_radius: float = 10.0) -> list[tuple[int, int]]:
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    points = []
    for idx in range(1, num_labels):
        if stats[idx, cv2.CC_STAT_AREA] >= min_area:
            cx, cy = centroids[idx]
            points.append((int(round(cx)), int(round(cy))))
    return _merge_close_points(points, merge_radius=merge_radius)


def extract_features(binary_mask: np.ndarray) -> tuple[np.ndarray, dict]:
    skeleton = skeletonize_mask(binary_mask)
    skel, neighbor_sum = _neighbor_counts(skeleton)

    intersections_mask = np.logical_and(skel == 1, neighbor_sum >= 4)
    endpoints_mask = np.logical_and(skel == 1, neighbor_sum == 1)

    intersections = _extract_cluster_centers(intersections_mask, min_area=3, merge_radius=12.0)
    endpoints = _extract_cluster_centers(endpoints_mask, min_area=2, merge_radius=8.0)

    feature_summary = {
        "intersection_count": len(intersections),
        "endpoint_count": len(endpoints),
        "intersections": intersections[:200],
        "endpoints": endpoints[:200],
    }
    return skeleton, feature_summary
