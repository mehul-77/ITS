import numpy as np
import cv2
from skimage.morphology import skeletonize


def skeletonize_mask(binary_mask: np.ndarray) -> np.ndarray:
    """
    Input: binary mask uint8 (0/255)
    Output: skeleton as uint8 (0/255)
    """
    bw = (binary_mask > 0).astype(np.uint8)
    skel_bool = skeletonize(bw > 0)
    skel = (skel_bool.astype(np.uint8)) * 255
    return skel


def count_intersections(skeleton_uint8: np.ndarray) -> int:
    """
    Intersection detection via neighbor counting on skeleton.
    Count skeleton pixels that have 3 or more skeleton neighbors (8-neighborhood).
    """
    skel = (skeleton_uint8 > 0).astype(np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)
    neighbor_sum = cv2.filter2D(skel, -1, kernel) - skel
    intersections = np.logical_and(skel == 1, neighbor_sum >= 3)
    return int(np.count_nonzero(intersections))


def extract_features(binary_mask: np.ndarray) -> tuple[np.ndarray, int]:
    skel = skeletonize_mask(binary_mask)
    intersections = count_intersections(skel)
    return skel, intersections
