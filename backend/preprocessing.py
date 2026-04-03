import cv2
import numpy as np
from typing import Tuple


def resize_image(image_bgr: np.ndarray, max_dim: int = 1024) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    max_curr = max(h, w)
    if max_curr <= max_dim:
        return image_bgr.copy()
    scale = max_dim / max_curr
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized


def to_grayscale(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def gaussian_blur(gray: np.ndarray, ksize: Tuple[int, int] = (5, 5)) -> np.ndarray:
    return cv2.GaussianBlur(gray, ksize, 0)


def clahe_enhance(gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)


def preprocess(image_bgr: np.ndarray, max_dim: int = 1024) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns: (resized_bgr, enhanced_gray)
    """
    resized = resize_image(image_bgr, max_dim=max_dim)
    gray = to_grayscale(resized)
    blurred = gaussian_blur(gray)
    enhanced = clahe_enhance(blurred)
    return resized, enhanced
