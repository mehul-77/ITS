import cv2
import numpy as np
from main import preprocess, detect_roads, extract_features, compute_all_metrics
from utils import image_to_base64
import os

img_path = r"c:/Users/DELL/Desktop/its proj/ITS-1/sample_images/test_satellite.jpg"
if not os.path.exists(img_path):
    print("Image not found")
else:
    img_bgr = cv2.imread(img_path)
    resized_bgr, enhanced_gray = preprocess(img_bgr, max_dim=1024)
    road_mask, _ = detect_roads(resized_bgr)
    skeleton, features = extract_features(road_mask)
    metrics = compute_all_metrics(road_mask, skeleton, features)
    
    print(f"Road density: {metrics['road_density_percent']} %")
    print(f"Intersection count: {metrics['intersection_count']}")
    
    mask_color = np.zeros_like(resized_bgr)
    mask_color[:, :, 2] = road_mask
    overlay = cv2.addWeighted(resized_bgr, 0.7, mask_color, 0.3, 0)
    
    # Draw intersections
    skel = (skeleton > 0).astype(np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)
    neighbor_sum = cv2.filter2D(skel, -1, kernel) - skel
    inters = np.logical_and(skel == 1, neighbor_sum >= 3)
    ys, xs = np.where(inters)
    for x, y in zip(xs, ys):
        cv2.circle(overlay, (x, y), radius=6, color=(0, 255, 255), thickness=1)
        
    cv2.imwrite("backend_verify.jpg", overlay)
    print("Saved backend_verify.jpg")
