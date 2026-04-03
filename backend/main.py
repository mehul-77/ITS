from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np

from preprocessing import preprocess
from road_detection import detect_roads
from feature_extraction import extract_features
from its_metrics import compute_all_metrics
from utils import pil_from_bytes, pil_to_cv2, image_to_base64, cv2_to_pil

app = FastAPI(title="Road Network ITS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pil = pil_from_bytes(contents)
        img_bgr = pil_to_cv2(pil)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    resized_bgr, enhanced_gray = preprocess(img_bgr, max_dim=1024)
    road_mask = detect_roads(enhanced_gray)
    skeleton, intersections = extract_features(road_mask)
    metrics = compute_all_metrics(road_mask, skeleton, intersections)

    try:
        mask_color = np.zeros_like(resized_bgr)
        mask_color[:, :, 2] = road_mask
        overlay = cv2_add_weighted_safe(resized_bgr, mask_color, alpha=0.7, beta=0.3)
        vis = overlay.copy()
        inter_coords = get_intersection_coords(skeleton)
        for (x, y) in inter_coords:
            cv2.circle(vis, (x, y), radius=6, color=(0, 255, 255), thickness=1)
        processed_b64 = image_to_base64(vis, fmt="png")
    except Exception:
        processed_b64 = image_to_base64(road_mask, fmt="png")

    response = {
        "processed_image": processed_b64,
        "road_density": metrics["road_density"],
        "road_length": metrics["road_length"],
        "intersection_count": metrics["intersection_count"],
    }
    return response


def cv2_add_weighted_safe(img1, img2, alpha=0.7, beta=0.3):
    import cv2
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_NEAREST)
    img1_u8 = img1.astype("uint8")
    img2_u8 = img2.astype("uint8")
    return cv2.addWeighted(img1_u8, alpha, img2_u8, beta, 0)


def get_intersection_coords(skeleton_uint8):
    """
    Return list of (x, y) coords of intersection pixels to plot.
    Uses same neighbor counting method as feature_extraction.
    """
    import numpy as np
    import cv2
    skel = (skeleton_uint8 > 0).astype(np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)
    neighbor_sum = cv2.filter2D(skel, -1, kernel) - skel
    intersections = np.logical_and(skel == 1, neighbor_sum >= 3)
    ys, xs = np.where(intersections)
    coords = list(zip(xs.tolist(), ys.tolist()))
    return coords


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
