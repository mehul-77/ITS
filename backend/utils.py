import base64
import io
from PIL import Image
import numpy as np
import cv2


def pil_from_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def pil_to_cv2(img_pil: Image.Image) -> np.ndarray:
    arr = np.array(img_pil)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    if len(cv_img.shape) == 2:
        mode = "L"
        return Image.fromarray(cv_img, mode=mode)
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def image_to_base64(cv_img: np.ndarray, fmt: str = "png") -> str:
    """
    Returns data URI string like 'data:image/png;base64,...'
    Accepts 2D or 3-channel BGR cv2 images.
    """
    if cv_img.dtype != np.uint8:
        cv_img = (np.clip(cv_img, 0, 1) * 255).astype(np.uint8)
    success, buffer = cv2.imencode(f".{fmt}", cv_img)
    if not success:
        raise ValueError("Failed to encode image")
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/{fmt};base64,{b64}"


def base64_to_pil(b64str: str) -> Image.Image:
    header, encoded = b64str.split(",", 1) if "," in b64str else ("", b64str)
    data = base64.b64decode(encoded)
    return pil_from_bytes(data)
