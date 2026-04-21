# First Review Report

## 1. Title

**Automated Satellite Feature Extraction and Intelligent Transportation System Readiness Assessment for Indian Urban Corridors**

## 2. Background & Motivation

Rapid urbanization in India has increased traffic congestion, travel delays, fuel consumption, and pressure on existing transport infrastructure. Intelligent Transportation Systems (ITS) support better mobility through data-driven planning, traffic monitoring, signal optimization, incident response, and corridor management. However, many student and planning projects depend on expensive datasets, field-heavy surveys, or highly specialized tools.

This project addresses that gap by building an automated and presentation-ready workflow that combines satellite image interpretation with road-network analytics. The idea is to detect and analyze transportation features from remotely sensed imagery and open map data so that planners can quickly assess road density, connectivity, intersections, and urban readiness for ITS deployment in Indian cities.

The project is framed around India because Indian cities show large variation in road width, informal growth patterns, mixed land use, and heterogeneous infrastructure quality. A low-cost, reproducible pipeline based on open-source tools can therefore be valuable for academic work, smart-city studies, and transport planning demonstrations.

## 3. Objectives

The major objectives of the project are:

- To build an automated feature extraction pipeline for satellite road imagery.
- To improve the accuracy of road reading from satellite scenes using hybrid image-processing methods.
- To integrate extracted features with Intelligent Transportation System core topics such as road hierarchy, connectivity, density, and intersection analysis.
- To create an India-focused analysis dashboard that combines map-based and image-based transport insights.
- To generate a first-review-report and presentation-ready outputs suitable for academic evaluation.

## 4. Methodology

### Data

The project uses two main data sources:

- Publicly available satellite images for road-scene interpretation and visual feature extraction.
- OpenStreetMap road network data for Indian cities such as Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata, Ahmedabad, and Surat.

The selected datasets help cover both image understanding and transport-network analytics. Satellite imagery gives scene-level visual evidence, while map data supports road hierarchy, connectivity, and corridor measurements.

### Approach/Algorithms

The proposed workflow follows these stages:

1. **Image preprocessing**
   Satellite images are resized, denoised, contrast-enhanced, and normalized to improve road visibility under shadow, mixed textures, and urban clutter.

2. **Hybrid road extraction**
   A fusion-based method is used instead of relying on a single thresholding step. The new pipeline combines:
   - Ridge detection using Frangi filtering
   - Surface-based cues from low saturation and neutral road color patterns
   - Edge-based support using Canny edge detection
   - Morphological filtering and connected-component cleanup

3. **Feature extraction**
   The extracted road mask is skeletonized to derive structural transport features:
   - Road length estimate
   - Intersection points
   - Endpoints and dead-end tendencies
   - Connectivity indicators

4. **ITS-oriented network analytics**
   For city-level analysis, OpenStreetMap road data is processed to estimate:
   - Road hierarchy distribution
   - Total corridor length
   - Road density
   - Connectivity index
   - ITS readiness level

5. **Dashboard and automated tools**
   The backend is implemented using FastAPI and image-processing libraries, while the frontend uses Next.js. The dashboard now supports:
   - Indian city presets
   - Interactive map layers
   - Satellite image upload and automated extraction
   - Visual outputs for road mask, enhanced image, and skeleton network
   - Downloadable report and GeoJSON outputs

### Evaluation

The first review stage focuses on practical and visual evaluation rather than final benchmark reporting. The project will be evaluated using:

- Visual correctness of extracted roads from sample satellite images
- Continuity of road segments after cleanup
- Reasonable estimation of intersections and endpoints
- Quality of road hierarchy and density indicators from city-level analysis
- Relevance of outputs to ITS topics in the Indian planning context

At later stages, the evaluation can be strengthened using annotated benchmark images, georeferenced datasets, or comparison with manually verified road segments.

## 5. Expected Outcomes

The expected outcomes of the project are:

- A complete revamped ITS feature extraction project tailored to Indian urban use cases
- Improved satellite-image reading accuracy compared to a basic single-method pipeline
- Automated extraction of roads, intersections, and connectivity features
- An integrated dashboard that combines transport-network analytics and image-based inference
- Presentation-ready report content for faculty review
- A strong foundation for future extension into traffic forecasting, route planning, smart intersections, and urban infrastructure monitoring

## 6. Timeline/Milestones

| Phase | Milestone | Expected Output |
|---|---|---|
| Phase 1 | Literature review and problem definition | Review notes and India-focused project framing |
| Phase 2 | Data collection and sample city selection | Satellite samples and city coordinate presets |
| Phase 3 | Image preprocessing and road extraction | Improved road mask generation |
| Phase 4 | Feature extraction and ITS metric design | Intersections, density, connectivity indicators |
| Phase 5 | Dashboard integration and automation tools | Full-stack prototype |
| Phase 6 | Validation, report preparation, and presentation | Final review material and demo outputs |

## 7. Resources & Budget

### Resources

- OpenStreetMap road network data
- Public satellite imagery
- Python, OpenCV, scikit-image, NumPy, FastAPI
- Next.js and React for frontend visualization
- Standard laptop or lab workstation

### Budget

This project is intentionally designed as a low-cost implementation. Since the workflow relies mostly on open-source tools and public data, the expected budget is minimal.

| Item | Estimated Cost |
|---|---|
| Open-source software stack | Rs. 0 |
| Public map and satellite sources | Rs. 0 |
| Existing laptop/lab system | Already available |
| Optional cloud hosting/demo deployment | Rs. 0 to Rs. 2,000 |

## 8. References

1. OpenStreetMap Contributors, OpenStreetMap road network data.
2. Standard literature on Intelligent Transportation Systems and smart-city mobility planning.
3. Remote sensing and satellite image processing references for road extraction and segmentation.
4. OpenCV and scikit-image documentation for image enhancement, edge detection, morphology, and skeletonization.
5. Research studies on transportation-network feature extraction from remotely sensed imagery.
