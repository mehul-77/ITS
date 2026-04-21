---
library_name: transformers
tags:
  - segformer
  - semantic-segmentation
  - satellite-imagery
  - remote-sensing
  - land-use
  - geospatial
  - nepal
  - kathmandu
license: mit
language:
  - en
pipeline_tag: image-segmentation
---

# Model Card — SegFormer-B0 Kathmandu Valley Satellite Segmentation

## Model Description

This model is a fine-tuned **SegFormer-B0** for semantic segmentation of satellite imagery over **Kathmandu Valley, Nepal**. It classifies each pixel into one of 7 land-use categories: Background, Residential Area, Road, River, Forest, and Unused Land. The model is intended for urban planning, GIS analysis, and geospatial research applications.

- **Developed by:** [praniil](https://github.com/praniil)
- **Model type:** Semantic Segmentation (SegFormer-B0)
- **Language(s) (NLP):** N/A (Computer Vision)
- **License:** MIT
- **Finetuned from model:** `nvidia/mit-b0` (SegFormer-B0 pretrained on ImageNet)

### Model Sources

- **Repository:** [https://github.com/praniil/satellite-image-segmentation](https://github.com/praniil/satellite-image-segmentation)
- **HuggingFace Hub:** `Pranilllllll/segformer-satellite-segementation`

---

## Uses

### Direct Use

This model can be used out-of-the-box for **satellite image segmentation** over Kathmandu Valley or similar urban/semi-urban landscapes. It accepts a 512×512 RGB satellite image and outputs a per-pixel land-use classification mask.
```python
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from transformers import SegformerForSemanticSegmentation, SegformerFeatureExtractor

device = "cuda" if torch.cuda.is_available() else "cpu"

HF_REPO = "Pranilllllll/segformer-satellite-segementation"
model = SegformerForSemanticSegmentation.from_pretrained(HF_REPO).to(device)
processor = SegformerFeatureExtractor.from_pretrained(HF_REPO)
model.eval()

image = Image.open("path_to_your_satellite_image.png").convert("RGB")
inputs = processor(images=image, return_tensors="pt")
pixel_values = inputs["pixel_values"].to(device)

with torch.no_grad():
    outputs = model(pixel_values=pixel_values)
    logits = outputs.logits  # [1, 7, H, W]

pred_mask = torch.argmax(logits, dim=1).squeeze().cpu().numpy()

colors = np.array([
    [0, 0, 0],       # Background
    [128, 0, 0],     # Residential Area
    [0, 128, 0],     # Road
    [0, 0, 128],     # River
    [0, 128, 128],   # Forest
    [128, 128, 0],   # Unused Land
    [128, 0, 128],   # (reserved)
], dtype=np.uint8)

seg_image = colors[pred_mask]
plt.imsave("prediction.png", seg_image)
print("Inference complete. Prediction saved as prediction.png")
```

### Downstream Use

This model can be plugged into larger GIS pipelines for:
- Automated land-use/land-cover (LULC) mapping
- Urban sprawl analysis
- River and forest change detection
- Input feature generation for spatial planning models

### Out-of-Scope Use

- Not suitable for segmenting non-satellite imagery (street photos, drone footage with different resolution/angle).
- Performance may degrade on satellite imagery from regions with significantly different land cover patterns than Kathmandu Valley.
- Not suitable for fine-grained object detection within classes (e.g., identifying individual buildings).

---

## Bias, Risks, and Limitations

- **Geographic bias:** Trained exclusively on Kathmandu Valley tiles; may not generalize to other geographies.
- **Class imbalance:** Despite weighted loss, rare classes (Road, River) may have lower per-class IoU.
- **Resolution dependency:** Expects 512×512 input tiles; other resolutions require resizing and may affect accuracy.
- **Annotation noise:** Manual annotations via CVAT may have some boundary ambiguity between classes.

### Recommendations

Validate predictions on your specific region before using results for critical planning decisions. Cross-checking against GIS datasets (e.g., OpenStreetMap) is recommended.

---

## How to Get Started with the Model

Install dependencies:
```bash
pip install torch transformers Pillow matplotlib
```

Then use the inference script in the Direct Use section above.

---

## Training Details

### Training Data

A custom dataset was built from satellite imagery of **Kathmandu Valley, Nepal**, divided into a grid of tiles.

- **Total images:** ~400 tiles
- **Resolution:** 512 × 512 pixels
- **Annotation tool:** [CVAT](https://github.com/opencv/cvat)
- **Task:** Multi-class semantic segmentation

#### Annotation Classes

| Class ID | Class Name       | RGB Color       |
|----------|------------------|-----------------|
| 0        | Background       | (0, 0, 0)       |
| 1        | Residential Area | (128, 0, 0)     |
| 2        | Road             | (0, 128, 0)     |
| 3        | River            | (0, 0, 128)     |
| 4        | Forest           | (0, 128, 128)   |
| 5        | Unused Land      | (128, 128, 0)   |

### Training Procedure

#### Preprocessing

- Images resized to 512 × 512
- Standard ImageNet normalization via `SegformerFeatureExtractor`

#### Data Augmentation

Applied using `albumentations`:
- Horizontal and vertical flips
- Random 90-degree rotations
- Resize to 512 × 512

#### Training Hyperparameters

| Hyperparameter   | Value                              |
|------------------|------------------------------------|
| Input size       | 512 × 512                          |
| Batch size       | 16                                 |
| Optimizer        | AdamW                              |
| Learning rate    | 3e-5                               |
| Loss function    | Weighted Cross-Entropy             |
| Epochs           | 300 (early stopping, patience=25)  |
| Cross-validation | 3-fold                             |
| Training regime  | bf16 mixed precision               |

#### Class Imbalance Handling

Inverse frequency class weights were computed from the training set and applied to the cross-entropy loss, ensuring rare classes (Road, River) contribute proportionally during training.

---

## Evaluation

### Metrics

- **Mean IoU (mIoU):** Primary metric — overlap between predicted and ground truth masks averaged across all classes.
- **Per-class IoU:** Segmentation accuracy per land-use category.
- **Qualitative inspection:** Visual comparison of predicted vs. ground truth masks.

### Results

Cross-validation results are reported as **mean ± standard deviation of mIoU** across 3 folds. Training curves (loss, mIoU, gradient norm) are available in the [`eval_plots/`](https://github.com/praniil/satellite-image-segmentation/tree/main/eval_plots) directory.

The stable gradient norm across training confirms the MiT encoder converged effectively without vanishing gradient issues.

---

## Model Architecture

- **Backbone:** SegFormer-B0 (`nvidia/mit-b0`)
- **Encoder:** MiT (Mix Transformer) — hierarchical global context without positional encoding
- **Decoder:** Lightweight MLP head — per-pixel class probability predictions
- **Output:** 7-class segmentation mask over a 512×512 spatial grid

---

## Environmental Impact

- **Hardware Type:** CUDA-enabled GPU
- **Cloud Provider:** Not applicable (local training)
- **Compute Region:** Nepal
- **Carbon Emitted:** Not measured

---

## Citation
```bibtex
@misc{praniil2024kathmandu-segmentation,
  author       = {praniil},
  title        = {Kathmandu Valley Satellite Image Segmentation with SegFormer-B0},
  year         = {2024},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/praniil/satellite-image-segmentation}},
}
```

---

## Model Card Authors

[praniil](https://github.com/praniil)

## Model Card Contact

Open an issue at [https://github.com/praniil/satellite-image-segmentation/issues](https://github.com/praniil/satellite-image-segmentation/issues)