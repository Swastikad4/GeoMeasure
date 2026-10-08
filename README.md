# Geospatial File Measurement API

A production-quality, minimal full-stack geospatial processing system built with **FastAPI**, **GeoPandas**, and **React (Vite)**. The application enables users to upload `.kml` and `.zip` (Shapefile) archives, extracts vector geospatial features, dynamically projects geographic coordinates to local metric CRS (UTM zones), calculates accurate metric measurements (polygon area and line length), and inspects results on an interactive map.

The user interface follows a refined aesthetic palette inspired by coastal nautical cartography and artisanal rosé wine labels (featuring muted slate blues, blush rose accents, and cool silver-gray paper tones).

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [File Processing Pipeline](#file-processing-pipeline)
5. [CRS Handling Strategy](#crs-handling-strategy)
6. [API Documentation](#api-documentation)
7. [Local Setup & Running](#local-setup--running)
8. [Docker Support](#docker-support)
9. [Design Decisions](#design-decisions)
10. [Testing](#testing)
11. [What Was Learned](#what-was-learned)
12. [Future Scope](#future-scope)

---

## 1. Features

- **Multi-Format Ingestion**: Supports `.kml` (Keyhole Markup Language) and `.zip` archives containing ESRI Shapefile sets (`.shp`, `.shx`, `.dbf`, `.prj`).
- **Safe Archive Unpacking**: Defends against Zip Slip directory traversal vulnerabilities during archive extraction.
- **Dynamic Projected CRS Transformation**: Automatically converts spherical WGS 84 (`EPSG:4326`) degree coordinates into optimal metric UTM projections for accurate metric calculations.
- **Measurement Engine**:
  - **Polygon / MultiPolygon**: Area in square meters ($m^2$) and hectares / square kilometers.
  - **LineString / MultiLineString**: Geodesic length in meters ($m$) and kilometers.
  - **Point / MultiPoint**: Non-measurable point entities handled cleanly without errors.
  - **Unsupported Geometries**: Gracefully flagged without server crashes.
- **Aggregated Analytics**: Live summaries of polygon area totals, cumulative line lengths, and geometry count breakdowns.
- **Interactive Map Preview**: Leaflet map preview with automatic bounding-box fitting and feature inspection popups.
- **Lightweight Metadata Persistence**: SQLite database persistence for file records without storing bulky raw geometry blobs.
- **Pre-Packaged Samples**: Quick-test buttons to immediately test sample KML and Shapefile files.

---

## 2. Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Spatial Engine**: GeoPandas, Shapely 2.x, PyProj, Pyogrio
- **Validation**: Pydantic v2
- **Database**: SQLite3
- **ASGI Server**: Uvicorn

### Frontend
- **Framework**: React 19 + Vite
- **HTTP Client**: Axios
- **Mapping**: Leaflet & React-Leaflet
- **Icons**: Lucide React
- **Styling**: Vanilla CSS (CSS Variables Design System)

---

## 3. Architecture

```text
[ Browser / React Client ]
       │
       │ HTTP / Multipart Form Data
       ▼
[ FastAPI Application (main.py) ]
       │
       ├── CORS & Security Layer (Zip Slip sanitizer, Size limit)
       │
       ├── [ File Service ] ─── extracts & writes to ──> [ uploads/ directory ]
       │
       ├── [ Geospatial Service ] ──> [ GeoPandas & Pyogrio ]
       │                                     │
       │                                     ▼
       │                            [ PyProj / CRS Service ]
       │                            (Detects CRS & Transforms to UTM)
       │                                     │
       │                                     ▼
       │                           [ Measurement Service ]
       │                           (Calculates Area m² & Length m)
       │
       ├── [ SQLite Database ] <── stores metadata (ID, status, CRS, counts)
       │
       └── JSON API Response (features, measurements, GeoJSON preview)
```

---

## 4. File Processing Pipeline

1. **Upload & Validation**: Validates file extension (`.kml`, `.zip`) and size limit (configurable up to 25 MB).
2. **Safe Storage**: Generates a unique 12-character alphanumeric ID and creates an isolated sandbox directory.
3. **Archive Unpacking**: If a `.zip` file is received, validates each internal path against directory traversal before extracting, then locates the primary `.shp` Shapefile.
4. **GeoDataFrame Parsing**: GeoPandas reads the dataset using high-performance GDAL/pyogrio drivers.
5. **CRS Detection**: Reads spatial reference metadata; if missing, falls back to EPSG:4326 with a clear user notice.
6. **Metric Projection**: Computes geometry centroids and transforms coordinates into the optimal local UTM zone.
7. **Measurement Calculation**: Shapely calculates planar area ($m^2$) or length ($m$) in metric units.
8. **Cache & Persistence**: Stores summary and metadata in SQLite and cached feature JSON.

---

## 5. CRS Handling Strategy

### Why Latitude & Longitude Cannot Directly Calculate Area and Distance
Geographic Coordinate Systems (such as **WGS 84 / EPSG:4326**) express positions in angular units (**degrees**). Because the Earth is roughly an oblate spheroid:
- One degree of longitude spans approximately $111\text{ km}$ at the equator, but decreases to $0\text{ km}$ at the poles ($\sim 111 \times \cos(\text{latitude})\text{ km}$).
- Planar calculation formulas applied directly to degree coordinates produce distorted, invalid values in $\text{degrees}^2$ rather than square meters.

### The Solution: Dynamic UTM Projection
1. **Source Detection**: The application inspects the file's native Coordinate Reference System via PyProj.
2. **Optimal Projected CRS Selection**:
   - If the dataset is geographic, `GeoPandas.estimate_utm_crs()` evaluates the centroid of the vector features to determine the best local Universal Transverse Mercator (UTM) zone (e.g. `EPSG:32632` or `EPSG:32633`).
   - UTM projections minimize both scale distortion and area deformation locally within a $6^\circ$ longitudinal zone.
   - If geometries span a wide global area or across multiple zones, the pipeline falls back to cylindrical equal-area projections (`EPSG:6933`) to ensure area calculations remain unbiased.
3. **Transformation**: `gdf.to_crs(utm_crs)` converts coordinates into Cartesian meters before calling `.area` or `.length`.
4. **Missing CRS Resilience**: When a Shapefile lacks a `.prj` file, the system flags a warning, infers WGS 84, and continues processing without crashing.

---

## 6. API Documentation

Swagger interactive documentation is automatically available at:
`http://localhost:8000/docs`

### 1. Upload Geospatial File
- **Endpoint**: `POST /api/files/`
- **Content-Type**: `multipart/form-data`
- **Request Body**: `file` (binary `.kml` or `.zip`)

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": "e9a03b54fd12",
    "filename": "berlin_parcels.zip",
    "file_type": "Shapefile (ZIP)",
    "feature_count": 2,
    "crs": "EPSG:4326",
    "status": "COMPLETED",
    "warning_message": null,
    "summary": {
      "total_features": 2,
      "polygon_count": 2,
      "line_count": 0,
      "point_count": 0,
      "unsupported_count": 0,
      "total_polygon_area_sqm": 242095.42,
      "total_line_length_m": 0.0
    },
    "created_at": "2026-10-09T02:27:00+00:00"
  },
  "message": "File processed successfully"
}
```

### 2. Get File Information
- **Endpoint**: `GET /api/files/{id}/`

### 3. Get Features
- **Endpoint**: `GET /api/files/{id}/features/`

**Response Example:**
```json
{
  "success": true,
  "data": {
    "file_id": "e9a03b54fd12",
    "crs": "EPSG:4326",
    "feature_count": 2,
    "features": [
      {
        "feature_id": 0,
        "geometry_type": "Polygon",
        "properties": {
          "id_code": "PLG-01",
          "name": "Berlin Mitte Sector"
        },
        "measurement": {
          "type": "area",
          "value": 150020.15,
          "unit": "m²",
          "message": null
        },
        "geometry_geojson": {
          "type": "Polygon",
          "coordinates": [...]
        }
      }
    ]
  },
  "message": "Features retrieved successfully"
}
```

### 4. Get Measurements
- **Endpoint**: `GET /api/files/{id}/measurements/`

### 5. Health Check
- **Endpoint**: `GET /api/health`
- **Response**: `{"status": "ok"}`

---

## 7. Local Setup & Running

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### Backend Setup

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   - **Windows PowerShell**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Backend will be running at `http://localhost:8000`.

---

### Frontend Setup

1. Open a second terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Frontend will be running at `http://localhost:5173`.

---

## 8. Docker Support

To run the complete system with Docker Compose:

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API & Swagger: `http://localhost:8000/docs`

---

## 9. Design Decisions

- **FastAPI**: Provides automatic OpenAPI Swagger documentation, async file streaming, and high throughput.
- **GeoPandas + Pyogrio**: Delivers C-level GDAL vector reading speeds for both KML and ESRI Shapefiles without needing complex external map servers.
- **Dynamic UTM Estimation**: Using `estimate_utm_crs()` ensures locally conformal and accurate planar measurements without hardcoding standard web mercator (EPSG:3857), which causes heavy latitude-dependent area distortions.
- **Lightweight SQLite Storage**: Stores operational file metadata without bloating the database with massive spatial geometry coordinates.
- **Zip Slip Defense**: Validates canonical resolved paths for each zip member before unpacking to prevent unauthorized filesystem writes.

---

## 10. Testing

Run the automated backend test suite with `pytest`:

```bash
# In backend directory or root with PYTHONPATH=backend
python -m pytest backend/tests/test_api.py -v
```

All 11 unit & integration tests verify:
1. Health endpoint status
2. KML file ingestion & metric calculation
3. Shapefile ZIP ingestion & metric calculation
4. Polygon area measurement logic ($m^2$)
5. LineString length measurement logic ($m$)
6. Point geometry null handling
7. Invalid file extension rejection (HTTP 400)
8. Corrupted KML error handling (HTTP 422)
9. Missing CRS detection & warning generation
10. Unsupported geometry handling
11. 404 response for nonexistent file IDs

---

## 11. What Was Learned

- **CRS Projection Dynamics**: The critical importance of differentiating between geographic angular coordinates (EPSG:4326) and projected metric coordinates (UTM / EPSG:6933) to calculate accurate physical ground units.
- **Secure File Ingestion**: Guarding against zip-slip directory traversal vulnerabilities and memory exhaustion through streaming chunk validation.
- **Format Nuances**: Handling ESRI Shapefile single-layer geometry constraints versus KML multi-geometry documents.

---

## 12. Future Scope

- **Background Celery / Redis Workers**: Offloading ultra-large multi-gigabyte GIS datasets to asynchronous background workers.
- **PostgreSQL / PostGIS Storage**: Enterprise-grade spatial indexing and complex spatial intersections.
- **Additional Geometry Metrics**: Perimeter calculation, polygon centroid analysis, bounding box extents, and elevation profile extraction for 3D KML features.
