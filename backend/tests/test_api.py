import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from shapely.geometry import GeometryCollection, Point, Polygon, LineString

from app.main import app
from app.services.measurement_service import MeasurementService
from app.services.crs_service import CRSService
import geopandas as gpd

client = TestClient(app)
SAMPLE_DIR = Path(__file__).parent.parent.parent / "sample_data"

def test_1_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_2_valid_kml_upload():
    kml_path = SAMPLE_DIR / "sample_polygon.kml"
    assert kml_path.exists(), f"Sample file {kml_path} missing"

    with open(kml_path, "rb") as f:
        response = client.post(
            "/api/files/",
            files={"file": ("sample_polygon.kml", f, "application/vnd.google-earth.kml+xml")}
        )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "COMPLETED"
    assert data["feature_count"] >= 1
    assert "EPSG:" in data["crs"]
    assert data["summary"]["polygon_count"] >= 1
    assert data["summary"]["total_polygon_area_sqm"] > 0

    # Test file details endpoint
    file_id = data["id"]
    detail_res = client.get(f"/api/files/{file_id}/")
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["id"] == file_id

    # Test features endpoint
    feat_res = client.get(f"/api/files/{file_id}/features/")
    assert feat_res.status_code == 200
    assert len(feat_res.json()["data"]["features"]) == data["feature_count"]

    # Test measurements endpoint
    meas_res = client.get(f"/api/files/{file_id}/measurements/")
    assert meas_res.status_code == 200
    assert "measurements" in meas_res.json()["data"]

def test_3_valid_shapefile_zip_upload():
    zip_path = SAMPLE_DIR / "sample_shapefile.zip"
    assert zip_path.exists(), f"Sample file {zip_path} missing"

    with open(zip_path, "rb") as f:
        response = client.post(
            "/api/files/",
            files={"file": ("sample_shapefile.zip", f, "application/zip")}
        )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["file_type"] == "Shapefile (ZIP)"
    assert data["status"] == "COMPLETED"
    assert data["feature_count"] == 2
    assert data["summary"]["polygon_count"] == 2

def test_4_polygon_area_measurement():
    # Unit test measurement service for Polygon
    poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    geom_type, measurement = MeasurementService.calculate_measurement(poly)
    assert geom_type == "Polygon"
    assert measurement.type == "area"
    assert measurement.unit == "m²"
    assert measurement.value == 100.0

def test_5_linestring_length_measurement():
    # Unit test measurement service for LineString
    line = LineString([(0, 0), (10, 0), (10, 10)])
    geom_type, measurement = MeasurementService.calculate_measurement(line)
    assert geom_type == "LineString"
    assert measurement.type == "length"
    assert measurement.unit == "m"
    assert measurement.value == 20.0

def test_6_point_handling():
    # Unit test measurement service for Point
    pt = Point(5, 5)
    geom_type, measurement = MeasurementService.calculate_measurement(pt)
    assert geom_type == "Point"
    assert measurement.type is None
    assert measurement.value is None

def test_7_invalid_file_extension():
    response = client.post(
        "/api/files/",
        files={"file": ("malicious.exe", b"not-geospatial", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_8_corrupted_file_handling():
    corrupt_path = SAMPLE_DIR / "sample_corrupt.kml"
    with open(corrupt_path, "rb") as f:
        response = client.post(
            "/api/files/",
            files={"file": ("sample_corrupt.kml", f, "application/vnd.google-earth.kml+xml")}
        )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert "Processing error" in body["message"]

def test_9_missing_crs_handling():
    zip_no_prj = SAMPLE_DIR / "sample_missing_crs.zip"
    with open(zip_no_prj, "rb") as f:
        response = client.post(
            "/api/files/",
            files={"file": ("sample_missing_crs.zip", f, "application/zip")}
        )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    # Verify warning message about missing CRS
    data = body["data"]
    assert data["warning_message"] is not None
    assert "Warning" in data["warning_message"]
    assert "missing" in data["warning_message"].lower()

def test_10_unsupported_geometry():
    # A GeometryCollection or non-standard geometry
    collection = GeometryCollection([Point(0, 0), LineString([(0, 0), (1, 1)])])
    geom_type, measurement = MeasurementService.calculate_measurement(collection)
    assert geom_type == "GeometryCollection"
    assert measurement.value is None
    assert "Measurement is not supported" in measurement.message

def test_11_missing_file_id_not_found():
    response = client.get("/api/files/nonexistent_id_9999/")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
