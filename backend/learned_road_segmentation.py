from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor


MODEL_ID = "Pranilllllll/segformer-satellite-segementation"
ROAD_CLASS_ID = 2
MODEL_DIR = Path(__file__).resolve().parent / "models" / "segformer_satellite"

torch.set_grad_enabled(False)
try:
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
except Exception:
    pass


@lru_cache(maxsize=1)
def load_model_bundle():
    source = str(MODEL_DIR if MODEL_DIR.exists() else MODEL_ID)
    processor = SegformerImageProcessor.from_pretrained(source, local_files_only=MODEL_DIR.exists())
    model = SegformerForSemanticSegmentation.from_pretrained(source, local_files_only=MODEL_DIR.exists())
    model.eval()
    return processor, model


def detect_roads_with_model(img_bgr: np.ndarray) -> tuple[np.ndarray, dict]:
    processor, model = load_model_bundle()

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    inputs = processor(images=image, return_tensors="pt")

    with torch.inference_mode():
        outputs = model(**inputs)

    logits = outputs.logits
    upsampled = torch.nn.functional.interpolate(
        logits,
        size=img_bgr.shape[:2],
        mode="bilinear",
        align_corners=False,
    )
    prediction = upsampled.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)
    road_mask = np.where(prediction == ROAD_CLASS_ID, 255, 0).astype(np.uint8)

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
    min_area = max(32, int(img_bgr.shape[0] * img_bgr.shape[1] * 0.00004))
    kept = 0

    for idx in range(1, num_labels):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if area >= min_area:
            final_mask[labels == idx] = 255
            kept += 1

    metadata = {
        "method": "segformer_satellite_road_segmentation",
        "model_id": MODEL_ID,
        "road_class_id": ROAD_CLASS_ID,
        "components_kept": kept,
    }
    return final_mask, metadata
