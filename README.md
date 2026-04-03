# Intelligent Transportation System — Road Network Extraction

Project: Road Network Extraction from Satellite Imagery for ITS metrics.

This repository implements a modular, clean, and deployable pipeline that extracts road networks from satellite images using classical CV (no heavy ML training). It produces ITS metrics such as road density, approximate road length, and intersection count.

---

## Project Structure

```
road-network-its/
│
├── backend/
│   ├── preprocessing.py
│   ├── road_detection.py
│   ├── feature_extraction.py
│   ├── its_metrics.py
│   ├── utils.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/page.js
│   ├── components/ImageUpload.js
│
├── sample_images/
└── README.md
```

---

## ITS Concept

An Intelligent Transportation System (ITS) benefits from accurate road network maps extracted automatically from high-resolution satellite imagery. This project detects roads, produces a binary mask and skeleton, and extracts metrics useful for transportation planning: road density, estimated road length, and number of intersections.

---

## Methodology

### 1. Preprocessing
- Resize to reasonable dimensions (keeps CPU usage moderate).
- Convert to grayscale.
- Gaussian blur to reduce noise.
- CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance contrast.

### 2. Road Detection
- Otsu thresholding and Canny edge detection combined.
- Morphological closing / opening to clean and connect road segments.
- Produces a binary road mask.

### 3. Feature Extraction
- Skeletonize the binary mask using skimage.
- Detect intersections by counting skeleton neighbors (8-neighborhood).

### 4. ITS Metrics
- **Road density**: ratio of road pixels to total pixels.
- **Road length estimate**: count of skeleton pixels (approximate length in pixel units).
- **Intersection count**: number of skeleton junction pixels.

---

## Architecture

```
Frontend (Next.js on Vercel)
↓
Backend API (FastAPI on Render or similar)
↓
Image Processing Pipeline (OpenCV + scikit-image)
↓
ITS Metrics Extraction
```

The backend exposes a single endpoint:
- **POST** `/process-image`
- Input: form file (image)
- Output: JSON with processed image (base64 data URI) and metrics

---

## How to Run Locally

### Backend

1. Create and activate a virtualenv:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the server:
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend

1. Ensure Node 18+ and npm installed.

2. Scaffold a Next.js app or extract the provided files into an existing Next.js project:
   ```bash
   npx create-next-app@latest frontend
   ```

3. Replace `app/page.js` and create `components/ImageUpload.js` with the provided files.

4. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

5. Set environment variable and run:
   ```bash
   set NEXT_PUBLIC_API_URL=http://localhost:8000
   npm run dev
   ```

6. Open `http://localhost:3000` in your browser.

---

## Example Results

- **Processed image**: Road mask overlaid in red on the original satellite image.
- **Skeleton & intersections**: Visualized with yellow circles marking junction points.
- **Road density**: Fraction (0-1), displayed as percentage in the frontend.
- **Road length**: Measured in pixels (approximate).
- **Intersection count**: Number of junction points detected via skeleton neighbor analysis.

---

## Limitations

- **No geospatial scaling**: Road length is measured in pixels. For real-world units, georeferenced images and ground sampling distance (meters/pixel) are required.
- **Classical CV approach**: Can fail in complex scenarios (dense vegetation, shadows, small roads).
- **Intersection detection**: Simple neighbor counting may overcount in noisy skeletons.
- **Parameter tuning**: Thresholds and kernel sizes are heuristic and may need adjustment per dataset.
- **Performance**: CPU-friendly but can be slow for very large images; resizing mitigates this.

---

## Future Scope

- Add optional geospatial support (read GeoTIFF, use image ground sampling distance to report length in meters).
- Integrate a lightweight segmentation model (edge- or feature-based) for improved accuracy.
- Post-processing: graph extraction from skeleton to create routable road graph.
- Tile-based processing for very large images and parallelization.
- Add unit tests, CI/CD, Docker containerization, and production configuration.
- Advanced morphological operations for complex road scenarios.

---

## Deployment

### Backend Deployment (Render / Railway / Heroku)

1. Push code to GitHub.
2. Connect repository to Render/Railway/Heroku.
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Note the backend URL (e.g., `https://your-backend-app.onrender.com`).

### Frontend Deployment (Vercel)

1. Push code to GitHub.
2. Connect repository to Vercel.
3. Set root directory to `frontend/`.
4. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-app.onrender.com`
5. Deploy.

---

## Testing with Sample Images

1. Place satellite images in `sample_images/`.
2. Use the frontend to upload and process.
3. Verify metrics and visualizations.

Example with curl:
```bash
curl -X POST "http://localhost:8000/process-image" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_images/road_image.jpg"
```

---

## Code Quality

- Modular design: Each processing step is a separate, reusable function.
- Clean code: Readable, well-commented, and efficient.
- Type hints: Used throughout for clarity.
- Error handling: Graceful fallbacks and user-friendly error messages.
- Resume-worthy: Production-level structure suitable for portfolio.

---

## Dependencies

- **Backend**: FastAPI, Uvicorn, OpenCV, NumPy, scikit-image, Pillow
- **Frontend**: Next.js, React

---

## Author Notes

This project demonstrates:
- Full-stack development (Python backend + JavaScript frontend)
- Computer vision pipeline design
- API development and integration
- Modular architecture for scalability
- Production-ready code suitable for deployment

For improvements or custom configurations, refer to the methodology section and adjust parameters in `preprocessing.py` and `road_detection.py`.

---

## License

This project is open-source and available for educational and commercial use.
