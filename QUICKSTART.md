# Road Network ITS - Quick Start Guide

## Prerequisites
- Python 3.8+ (for backend)
- Node 18+ and npm (for frontend)
- Git

## Quick Setup (Windows)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup (New Terminal)

```bash
cd frontend

# Install npm dependencies
npm install

# Create/update .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Run frontend dev server
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Test the Application

1. Open `http://localhost:3000` in your browser
2. Click "Upload & Process"
3. Select a satellite image file
4. View results: processed image + road metrics

---

## File Structure

```
road-network-its/
├── backend/                  # Python FastAPI server
│   ├── preprocessing.py      # Image preprocessing
│   ├── road_detection.py     # Road detection algorithm
│   ├── feature_extraction.py # Skeleton & intersection detection
│   ├── its_metrics.py        # Metric calculations
│   ├── utils.py              # Image utilities
│   ├── main.py               # FastAPI app
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Next.js React app
│   ├── app/
│   │   ├── page.js          # Home page
│   │   └── layout.js        # Root layout
│   ├── components/
│   │   └── ImageUpload.js   # Upload component
│   ├── package.json         # Node dependencies
│   ├── next.config.js       # Next.js config
│   ├── .env.local           # Environment variables
│   └── .gitignore
│
├── sample_images/            # Place test images here
├── README.md                 # Full documentation
└── QUICKSTART.md             # This file
```

---

## API Endpoint

**POST** `/process-image`

**Request:**
- Body: multipart/form-data with key `file` (image file)

**Response:**
```json
{
  "processed_image": "data:image/png;base64,...",
  "road_density": 0.042153,
  "road_length": 45872,
  "intersection_count": 127
}
```

---

## System Processing Flow

```
User uploads image (Next.js frontend)
        ↓
POST /process-image (FastAPI backend)
        ↓
Preprocess: resize → grayscale → blur → CLAHE enhance
        ↓
Road Detection: Canny edges + Otsu threshold → morphological operations
        ↓
Feature Extraction: skeletonize → count intersections
        ↓
Metrics: calculate road density, road length, intersection count
        ↓
Visualization: overlay processed image with intersections (yellow circles)
        ↓
Return base64 image + JSON metrics
        ↓
Frontend displays results
```

---

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+: `python --version`
- Reactivate venv: `.venv\Scripts\activate`
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

### Frontend won't start
- Clear node modules: `rm -r node_modules && npm install`
- Ensure Node 18+: `node --version`
- Check `.env.local` exists and has correct API URL

### Image upload fails
- Check image format (PNG, JPG, JPEG, GIF supported)
- Ensure backend is running on `http://localhost:8000`
- Check browser console for CORS errors

### Processing is slow
- Reduce image size before uploading (max dimension 1024px)
- Check CPU usage; pipeline is CPU-only by design

---

## Deployment

### Backend (Render, Railway, or Heroku)
1. Push code to GitHub
2. Connect repository to hosting platform
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Note backend URL

### Frontend (Vercel or Netlify)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable to backend URL
4. Deploy

---

## Sample Image Testing

Place satellite imagery in `sample_images/` and upload via the frontend UI, or test directly with curl:

```bash
curl -X POST "http://localhost:8000/process-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_images/road_image.jpg"
```

---

## Performance Notes

- **CPU-friendly**: No ML model training, uses classical computer vision
- **Max image size**: 1024px (configurable, smaller = faster)
- **Processing time**: 0.5-2 seconds per image on modern hardware
- **Memory**: ~200-500 MB for typical satellite images

---

## Next Steps

1. Add test images to `sample_images/`
2. Experiment with image parameter tuning in backend (kernel sizes, thresholds)
3. Deploy to production cloud platforms
4. Extend with geospatial features (GeoTIFF, coordinate systems)

---

For detailed documentation, see **README.md**
