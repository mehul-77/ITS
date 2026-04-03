import cv2
import numpy as np


def canny_edges(gray: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
    return cv2.Canny(gray, low_threshold, high_threshold)


def otsu_threshold(gray: np.ndarray) -> np.ndarray:
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def morph_clean(binary: np.ndarray, kernel_size: int = 5, iterations_close: int = 2, iterations_dilate: int = 1) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=iterations_close)
    dilated = cv2.dilate(closed, kernel, iterations=iterations_dilate)
    opened = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, kernel, iterations=1)
    _, final = cv2.threshold(opened, 127, 255, cv2.THRESH_BINARY)
    return final


def detect_roads(enhanced_gray: np.ndarray) -> np.ndarray:
    """
    Input: enhanced grayscale image (uint8)
    Output: binary road mask (uint8 0/255)
    """
    edges = canny_edges(enhanced_gray)
    th = otsu_threshold(enhanced_gray)
    combined = cv2.bitwise_or(edges, th)
    cleaned = morph_clean(combined)
    return cleaned
