from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import numpy as np
import cv2

import json
import math
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from preprocessing import preprocess
from road_detection import detect_roads
from feature_extraction import extract_features
from its_metrics import compute_all_metrics
from utils import pil_from_bytes, pil_to_cv2, image_to_base64

app = FastAPI(title="India ITS Feature Extraction Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path(tempfile.gettempdir()) / "road_extraction"
TEMP_DIR.mkdir(exist_ok=True)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

ROAD_HIERARCHY = {
    "motorway":       {"level": 1, "color": "#e74c3c", "label": "Motorway"},
    "motorway_link":  {"level": 1, "color": "#e74c3c", "label": "Motorway Link"},
    "trunk":          {"level": 2, "color": "#e67e22", "label": "Trunk Road"},
    "trunk_link":     {"level": 2, "color": "#e67e22", "label": "Trunk Link"},
    "primary":        {"level": 3, "color": "#f1c40f", "label": "Primary Road"},
    "primary_link":   {"level": 3, "color": "#f1c40f", "label": "Primary Link"},
    "secondary":      {"level": 4, "color": "#2ecc71", "label": "Secondary Road"},
    "secondary_link": {"level": 4, "color": "#2ecc71", "label": "Secondary Link"},
    "tertiary":       {"level": 5, "color": "#00d4aa", "label": "Tertiary Road"},
    "tertiary_link":  {"level": 5, "color": "#00d4aa", "label": "Tertiary Link"},
    "residential":    {"level": 6, "color": "#3498db", "label": "Residential"},
    "service":        {"level": 7, "color": "#9b59b6", "label": "Service Road"},
    "unclassified":   {"level": 7, "color": "#7f8c8d", "label": "Unclassified"},
    "living_street":  {"level": 7, "color": "#1abc9c", "label": "Living Street"},
    "pedestrian":     {"level": 8, "color": "#95a5a6", "label": "Pedestrian"},
    "footway":        {"level": 8, "color": "#bdc3c7", "label": "Footway"},
    "cycleway":       {"level": 8, "color": "#16a085", "label": "Cycleway"},
    "path":           {"level": 9, "color": "#636e72", "label": "Path"},
    "track":          {"level": 9, "color": "#6c5ce7", "label": "Track"},
}

def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def bbox_from_center(lat, lon, radius_m):
    """Approximate bounding box from center + radius in meters."""
    d_lat = radius_m / 111320
    d_lon = radius_m / (111320 * math.cos(math.radians(lat)))
    return {
        "lat_min": lat - d_lat,
        "lat_max": lat + d_lat,
        "lon_min": lon - d_lon,
        "lon_max": lon + d_lon,
    }

def fetch_osm_roads(bbox, max_retries: int = 2):
    """Fetch roads from Overpass API with retry + endpoint fallback for reliability."""
    import time
    import urllib.parse
    query = f"""
    [out:json][timeout:40];
    (
      way["highway"]({bbox['lat_min']},{bbox['lon_min']},{bbox['lat_max']},{bbox['lon_max']});
    );
    out geom;
    """
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    last_err = None
    for endpoint in OVERPASS_URLS:
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"User-Agent": "ITS-RoadExtraction/2.0"},
        )
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code not in {429, 500, 502, 503, 504}:
                    break
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                last_err = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
    raise last_err

def road_length_km(geometry):
    """Calculate road length from a list of {lat, lon} nodes."""
    total = 0.0
    for i in range(1, len(geometry)):
        total += haversine(
            geometry[i - 1]["lat"], geometry[i - 1]["lon"],
            geometry[i]["lat"], geometry[i]["lon"],
        )
    return round(total, 4)

def build_analysis(osm_data, bbox, lat, lon, radius):
    """Process raw Overpass data into the structure the frontend expects."""
    elements = [e for e in osm_data.get("elements", []) if e["type"] == "way" and "geometry" in e]

    features = []
    type_totals = {}
    all_nodes = {}

    for way in elements:
        highway = way.get("tags", {}).get("highway", "unclassified")
        info = ROAD_HIERARCHY.get(highway, {"level": 7, "color": "#7f8c8d", "label": highway.replace("_", " ").title()})
        geom = way.get("geometry", [])
        length = road_length_km(geom)
        coords = [[pt["lon"], pt["lat"]] for pt in geom]

        for pt in geom:
            key = (round(pt["lat"], 6), round(pt["lon"], 6))
            if key not in all_nodes:
                all_nodes[key] = set()
            all_nodes[key].add(way["id"])

        name = way.get("tags", {}).get("name", "")
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "id": way["id"],
                "highway": highway,
                "name": name,
                "label": info["label"],
                "color": info["color"],
                "level": info["level"],
                "length_km": length,
            },
        })
        type_totals[highway] = type_totals.get(highway, 0) + length

    geojson = {"type": "FeatureCollection", "features": features}

    intersections = []
    dead_ends_list = []
    endpoint_counts = {}
    
    for way in elements:
        geom = way.get("geometry", [])
        if len(geom) < 2:
            continue
        for pt in [geom[0], geom[-1]]:
            key = (round(pt["lat"], 6), round(pt["lon"], 6))
            endpoint_counts[key] = endpoint_counts.get(key, 0) + 1

    for (nlat, nlon), way_ids in all_nodes.items():
        if len(way_ids) >= 3:
            intersections.append([nlat, nlon])
        key = (nlat, nlon)
        if len(way_ids) == 1 and endpoint_counts.get(key, 0) == 1:
            dead_ends_list.append([nlat, nlon])

    total_length = sum(type_totals.values())
    type_distribution = []
    for highway, length in sorted(type_totals.items(), key=lambda x: -x[1]):
        info = ROAD_HIERARCHY.get(highway, {"level": 7, "color": "#7f8c8d", "label": highway.replace("_", " ").title()})
        pct = round((length / total_length * 100) if total_length > 0 else 0, 1)
        type_distribution.append({
            "type": highway,
            "label": info["label"],
            "color": info["color"],
            "percent": pct,
            "length_km": round(length, 2),
        })

    area_km2 = math.pi * (radius / 1000) ** 2
    int_count = len(intersections)
    de_count = len(dead_ends_list)
    density = round(total_length / area_km2, 1) if area_km2 > 0 else 0
    connectivity = round(int_count / (int_count + de_count) * 100, 1) if (int_count + de_count) > 0 else 0

    if density > 15 and connectivity >= 65:
        its = {"label": "High", "desc": f"Dense, well-connected road network ({density} km/km², {connectivity}% connectivity). Excellent for full ITS deployment."}
    elif density > 8 and connectivity >= 50:
        its = {"label": "High", "desc": f"Good road network ({density} km/km², {connectivity}% connectivity). Well suited for ITS deployment."}
    elif connectivity >= 70:
        its = {"label": "Medium", "desc": f"Highly connected but moderately sparse network ({density} km/km², {connectivity}% connectivity). ITS feasible; road expansion recommended."}
    elif density > 5 or connectivity > 35:
        its = {"label": "Medium", "desc": f"Moderate road network ({density} km/km², {connectivity}% connectivity). ITS deployment feasible with targeted improvements."}
    else:
        its = {"label": "Low", "desc": f"Sparse, poorly-connected road network ({density} km/km², {connectivity}% connectivity). Significant infrastructure development needed for ITS."}

    summary = {
        "total_roads": len(elements),
        "total_length_km": round(total_length, 2),
        "road_density_km_km2": density,
        "intersection_count": int_count,
        "dead_end_count": de_count,
        "connectivity_index": connectivity,
        "its_readiness": its,
    }

    grid_n = 6
    lat_step = (bbox["lat_max"] - bbox["lat_min"]) / grid_n
    lon_step = (bbox["lon_max"] - bbox["lon_min"]) / grid_n
    cells = []
    max_cell_length = 0.001

    for row in range(grid_n):
        for col in range(grid_n):
            cell_lat_min = bbox["lat_min"] + row * lat_step
            cell_lat_max = cell_lat_min + lat_step
            cell_lon_min = bbox["lon_min"] + col * lon_step
            cell_lon_max = cell_lon_min + lon_step

            cell_length = 0
            for feat in features:
                for coord in feat["geometry"]["coordinates"]:
                    clon, clat = coord
                    if cell_lat_min <= clat <= cell_lat_max and cell_lon_min <= clon <= cell_lon_max:
                        cell_length += feat["properties"]["length_km"] / max(len(feat["geometry"]["coordinates"]), 1)
                        break

            cells.append({
                "bounds": {
                    "lat_min": round(cell_lat_min, 6),
                    "lat_max": round(cell_lat_max, 6),
                    "lon_min": round(cell_lon_min, 6),
                    "lon_max": round(cell_lon_max, 6),
                },
                "length_km": round(cell_length, 3),
            })
            max_cell_length = max(max_cell_length, cell_length)

    for cell in cells:
        cell["normalized"] = round(cell["length_km"] / max_cell_length, 3) if max_cell_length > 0 else 0
    zone_grid = cells

    return {
        "metrics": {
            "summary": summary,
            "type_distribution": type_distribution,
            "geojson": geojson,
            "intersections": intersections[:500],
            "dead_ends": dead_ends_list[:300],
        },
        "zone_grid": zone_grid,
    }

@app.get("/")
def root():
    return {
        "status": "ok",
        "version": "1.0",
        "message": "ITS Road Network API",
    }

# ==============================================================================
# EXISTING ENDPOINTS (From legacy ITS-1)
# ==============================================================================

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pil = pil_from_bytes(contents)
        img_bgr = pil_to_cv2(pil)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    resized_bgr, enhanced_gray = preprocess(img_bgr, max_dim=768)
    road_mask, detector_meta = detect_roads(resized_bgr)
    skeleton, features = extract_features(road_mask)
    metrics = compute_all_metrics(road_mask, skeleton, features)
    analysis_summary = summarize_satellite_analysis(metrics, detector_meta)

    mask_color = np.zeros_like(resized_bgr)
    mask_color[:, :, 1] = (road_mask > 0).astype(np.uint8) * 160
    mask_color[:, :, 2] = (road_mask > 0).astype(np.uint8) * 255
    overlay = cv2_add_weighted_safe(resized_bgr, mask_color, alpha=0.8, beta=0.35)

    vis = overlay.copy()
    for (x, y) in features["intersections"][:200]:
        cv2.circle(vis, (x, y), radius=6, color=(0, 255, 255), thickness=1)
    for (x, y) in features["endpoints"][:200]:
        cv2.circle(vis, (x, y), radius=4, color=(255, 140, 0), thickness=1)

    skeleton_bgr = np.zeros_like(resized_bgr)
    skeleton_bgr[:, :, 0] = (skeleton > 0).astype(np.uint8) * 255
    skeleton_bgr[:, :, 1] = (skeleton > 0).astype(np.uint8) * 220
    for (x, y) in features["intersections"][:200]:
        cv2.circle(skeleton_bgr, (x, y), radius=5, color=(0, 255, 255), thickness=1)

    response = {
        "processed_image": image_to_base64(vis, fmt="png"),
        "road_mask_image": image_to_base64(road_mask, fmt="png"),
        "skeleton_image": image_to_base64(skeleton_bgr, fmt="png"),
        "enhanced_image": image_to_base64(enhanced_gray, fmt="png"),
        "road_density": metrics["road_density"],
        "road_density_percent": metrics["road_density_percent"],
        "road_length": metrics["road_length"],
        "intersection_count": metrics["intersection_count"],
        "endpoint_count": metrics["endpoint_count"],
        "average_width_px": metrics["average_width_px"],
        "connectivity_score": metrics["connectivity_score"],
        "feature_summary": features,
        "pipeline": {
            "detector": detector_meta["method"],
            "steps": [
                "Contrast enhancement and noise suppression",
                "Fast classical road extraction with structural and line support",
                "Skeletonization and topological feature extraction",
                "ITS-oriented metric computation for transport planning",
            ],
        },
        "analysis_summary": analysis_summary,
        "use_cases": [
            "Road inventory support for Indian smart-city corridors",
            "Intersection hotspot review for signal optimization studies",
            "Preliminary transport-network screening from satellite scenes",
        ],
    }
    return response

def cv2_add_weighted_safe(img1, img2, alpha=0.7, beta=0.3):
    import cv2
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_NEAREST)
    img1_u8 = img1.astype("uint8")
    img2_u8 = img2.astype("uint8")
    return cv2.addWeighted(img1_u8, alpha, img2_u8, beta, 0)


def summarize_satellite_analysis(metrics: dict, detector_meta: dict | None = None) -> dict:
    detector_meta = detector_meta or {}
    density = metrics["road_density_percent"]
    width = metrics["average_width_px"]
    intersections = metrics["intersection_count"]
    connectivity = metrics["connectivity_score"]
    components = int(detector_meta.get("components_kept", 0) or 0)
    lines = int(detector_meta.get("corridor_lines", 0) or detector_meta.get("hough_lines", 0) or 0)

    if density < 6:
        coverage = "Low coverage"
    elif density < 16:
        coverage = "Moderate coverage"
    else:
        coverage = "Dense coverage"

    if width >= 10:
        road_profile = "Wide corridor or arterial-road dominant scene"
    elif width >= 5:
        road_profile = "Mixed urban street scene"
    else:
        road_profile = "Narrow lane or fragmented extraction"

    if intersections >= 25:
        pattern = "Grid-like or junction-heavy local network"
    elif intersections >= 8:
        pattern = "Moderately connected roadway pattern"
    else:
        pattern = "Few clear junctions detected"

    quality_score = 100
    if density < 3:
        quality_score -= 45
    elif density < 8:
        quality_score -= 25
    if components > 35:
        quality_score -= 25
    if lines < 20:
        quality_score -= 20
    if intersections == 0 and density > 6:
        quality_score -= 20
    if connectivity >= 0.98 and intersections > 12:
        quality_score -= 10
    quality_score = max(0, min(100, quality_score))

    if density > 35:
        confidence = "Low"
        caution = "Likely over-detection remains; validate visually before using these counts."
    elif density < 1 and intersections == 0:
        confidence = "Low"
        caution = "Road evidence is too weak; likely under-detection or unsuitable imagery."
    elif quality_score < 55:
        confidence = "Low"
        caution = "Roads were not picked up clearly; use this only as a rough visual screening result."
    elif 8 <= density <= 26 and width >= 6:
        confidence = "Medium"
        caution = "Extraction is suitable for screening and presentation; verify fine road boundaries manually."
    else:
        confidence = "Medium"
        caution = "Useful for screening and presentation, but still not a survey-grade road inventory."

    return {
        "coverage_class": coverage,
        "road_profile": road_profile,
        "network_pattern": pattern,
        "extraction_confidence": confidence,
        "quality_score": quality_score,
        "caution": caution,
        "planning_note": "Use this output for rapid ITS screening, corridor review, and feature comparison with map data.",
    }

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


# ==============================================================================
# NEW OSM ENDPOINTS (Added during dashboard integration)
# ==============================================================================

@app.get("/analyze")
async def analyze(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: float = Query(1500, description="Radius in meters"),
):
    """Fetch road network from OpenStreetMap and compute ITS metrics."""
    try:
        bbox = bbox_from_center(lat, lon, radius)
        osm_data = fetch_osm_roads(bbox)
        result = build_analysis(osm_data, bbox, lat, lon, radius)
        return JSONResponse(result)
    except urllib.error.HTTPError as e:
        if e.code in {429, 500, 502, 503, 504}:
            raise HTTPException(
                503,
                "OpenStreetMap road service is temporarily busy or timed out. Try again, or reduce the radius to 1000-1500 meters.",
            )
        raise HTTPException(500, f"OSM analysis failed: HTTP {e.code}")
    except Exception as e:
        raise HTTPException(500, f"OSM analysis failed: {str(e)}")

@app.get("/geojson")
async def export_geojson_endpoint(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1500),
):
    """Generate GeoJSON from OSM road data for download."""
    try:
        bbox = bbox_from_center(lat, lon, radius)
        osm_data = fetch_osm_roads(bbox)
        analysis = build_analysis(osm_data, bbox, lat, lon, radius)
        geojson = analysis["metrics"]["geojson"]

        output_path = str(TEMP_DIR / "roads.geojson")
        with open(output_path, "w") as f:
            json.dump(geojson, f, indent=2)

        return FileResponse(
            output_path,
            media_type="application/geo+json",
            filename="roads.geojson",
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/report")
async def generate_report_endpoint(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1500),
):
    """Generate a PDF infrastructure report from OSM data."""
    try:
        bbox = bbox_from_center(lat, lon, radius)
        osm_data = fetch_osm_roads(bbox)
        analysis = build_analysis(osm_data, bbox, lat, lon, radius)
        s = analysis["metrics"]["summary"]
        readiness_score = round(
            min(
                100,
                (min(s["road_density_km_km2"], 20) / 20 * 45)
                + (s["connectivity_index"] / 100 * 35)
                + (min(s["intersection_count"], 80) / 80 * 20),
            ),
            1,
        )

        output_path = str(TEMP_DIR / "its_report.pdf")

        # Build a simple PDF report using reportlab
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from datetime import datetime

        BLUE = colors.HexColor("#1a73e8")
        DARK = colors.HexColor("#0d1117")
        GREY = colors.HexColor("#5f6368")
        BORDER = colors.HexColor("#dadce0")
        LIGHT_BLUE = colors.HexColor("#e8f0fe")

        base_styles = getSampleStyleSheet()
        styles = {
            "title": ParagraphStyle("title", parent=base_styles["Title"], fontSize=22, textColor=DARK, fontName="Helvetica-Bold", alignment=TA_LEFT),
            "subtitle": ParagraphStyle("subtitle", parent=base_styles["Normal"], fontSize=11, textColor=GREY, spaceAfter=20),
            "section": ParagraphStyle("section", parent=base_styles["Heading1"], fontSize=13, textColor=BLUE, spaceBefore=18, spaceAfter=8, fontName="Helvetica-Bold"),
            "body": ParagraphStyle("body", parent=base_styles["Normal"], fontSize=10, textColor=DARK, spaceAfter=6, leading=15),
            "footer": ParagraphStyle("footer", parent=base_styles["Normal"], fontSize=8, textColor=GREY, alignment=TA_CENTER),
        }

        doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2.5*cm)
        story = []
        now = datetime.now().strftime("%d %B %Y, %H:%M")

        story.append(Paragraph("Road Network Infrastructure Report", styles["title"]))
        story.append(Paragraph(f"ITS Analysis  ·  {now}  ·  ({lat}, {lon}) radius {radius}m", styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=16))

        story.append(Paragraph("1. Location and Study Area", styles["section"]))
        location_table = [
            ["Field", "Value"],
            ["Latitude", f"{lat:.6f}"],
            ["Longitude", f"{lon:.6f}"],
            ["Radius", f"{radius} m"],
            ["Bounding Box", f"{bbox['lat_min']:.6f}, {bbox['lon_min']:.6f} to {bbox['lat_max']:.6f}, {bbox['lon_max']:.6f}"],
        ]
        lt = Table(location_table, colWidths=[6*cm, 10*cm])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
            ("BOX", (0, 0), (-1, -1), 1, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(lt)
        story.append(Spacer(1, 0.35*cm))

        story.append(Paragraph("2. Network Summary", styles["section"]))
        story.append(Paragraph(
            f"Analysis of the road network within {radius}m of ({lat:.4f}, {lon:.4f}) "
            f"using OpenStreetMap data.", styles["body"]
        ))

        td = analysis["metrics"]["type_distribution"]

        table_data = [
            ["Metric", "Value"],
            ["Total Roads", str(s["total_roads"])],
            ["Total Length", f"{s['total_length_km']} km"],
            ["Road Density", f"{s['road_density_km_km2']} km/km²"],
            ["Intersections", str(s["intersection_count"])],
            ["Dead Ends", str(s["dead_end_count"])],
            ["Connectivity Index", f"{s['connectivity_index']}%"],
            ["ITS Readiness", s["its_readiness"]["label"]],
            ["Readiness Score", f"{readiness_score} / 100"],
        ]
        t = Table(table_data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
            ("BOX", (0, 0), (-1, -1), 1, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph("3. Road Type Distribution", styles["section"]))
        type_table = [["Road Type", "Length (km)", "Percentage"]]
        for item in td[:10]:
            type_table.append([item["label"], str(item["length_km"]), f"{item['percent']}%"])
        t2 = Table(type_table, colWidths=[6*cm, 5*cm, 5*cm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
            ("BOX", (0, 0), (-1, -1), 1, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t2)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph("4. ITS Readiness Assessment", styles["section"]))
        story.append(Paragraph(f"<b>{s['its_readiness']['label']}</b> ({readiness_score}/100): {s['its_readiness']['desc']}", styles["body"]))
        story.append(Paragraph(
            "Score basis: road density contributes up to 45 points, connectivity contributes up to 35 points, "
            "and intersection availability contributes up to 20 points. This score is intended for planning screening, not statutory certification.",
            styles["body"],
        ))
        story.append(Spacer(1, 1*cm))

        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        story.append(Paragraph(f"Generated by ITS Road Network Analysis Tool  ·  NIT Surat  ·  {now}", styles["footer"]))

        doc.build(story)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="its_report.pdf",
        )
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
