import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
from app.services.crs_service import CRSService
from app.services.measurement_service import MeasurementService
from app.schemas.file_schema import FeatureInfo, MeasurementSummary

logger = logging.getLogger(__name__)

def clean_property_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (float, np.floating)) and np.isnan(v):
        return None
    if pd.isna(v):
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if hasattr(v, "item"):
        val = v.item()
        if isinstance(val, float) and np.isnan(val):
            return None
        return val
    return str(v) if not isinstance(v, (int, float, bool, str, list, dict)) else v

class GeospatialService:
    @staticmethod
    def read_geodataframe(file_path: Path) -> gpd.GeoDataFrame:
        """
        Reads a geospatial file (.kml or .shp from unzipped directory).
        """
        suffix = file_path.suffix.lower()
        if suffix == ".kml":
            try:
                # Try pyogrio engine first
                return gpd.read_file(str(file_path), engine="pyogrio")
            except Exception as e:
                logger.info(f"Pyogrio KML read failed, falling back to default engine: {e}")
                return gpd.read_file(str(file_path))
        elif suffix == ".shp":
            try:
                return gpd.read_file(str(file_path), engine="pyogrio")
            except Exception:
                return gpd.read_file(str(file_path))
        else:
            return gpd.read_file(str(file_path))

    @classmethod
    def process_geospatial_file(
        cls, file_path: Path
    ) -> Tuple[List[Dict[str, Any]], MeasurementSummary, Optional[str], Optional[str]]:
        """
        Loads the geospatial dataset, extracts features, calculates measurements,
        and aggregates summary statistics.
        Returns:
            (features_list, summary, crs_name, warning_message)
        """
        gdf = cls.read_geodataframe(file_path)
        
        # Detect and normalize CRS
        gdf, crs_name, warning = CRSService.detect_and_normalize_crs(gdf)

        if gdf.empty:
            summary = MeasurementSummary(total_features=0)
            return [], summary, crs_name, warning

        # Project for measurement
        projected_gdf, projected_crs_name = CRSService.transform_to_projected_for_measurement(gdf)

        # Prepare WGS84 for GeoJSON mapping preview if possible
        try:
            wgs84_gdf = gdf.to_crs("EPSG:4326")
        except Exception:
            wgs84_gdf = gdf

        features_data: List[Dict[str, Any]] = []

        for idx in range(len(gdf)):
            # Original and projected geometries
            proj_geom = projected_gdf.geometry.iloc[idx] if idx < len(projected_gdf) else None
            wgs_geom = wgs84_gdf.geometry.iloc[idx] if idx < len(wgs84_gdf) else None

            # Calculate measurement on projected geometry
            geom_type, measurement = MeasurementService.calculate_measurement(proj_geom)

            # Extract and clean attributes/properties
            row_dict = gdf.iloc[idx].to_dict()
            properties = {
                k: clean_property_value(v)
                for k, v in row_dict.items()
                if k != "geometry"
            }

            # GeoJSON geometry representation for Leaflet preview
            geojson_geom = None
            if wgs_geom is not None and not wgs_geom.is_empty:
                try:
                    geojson_geom = mapping(wgs_geom)
                except Exception:
                    geojson_geom = None

            feature_dict = {
                "feature_id": int(idx),
                "geometry_type": geom_type,
                "properties": properties,
                "measurement": measurement.model_dump(),
                "geometry_geojson": geojson_geom
            }
            features_data.append(feature_dict)

        # Aggregate summary
        summary = MeasurementService.aggregate_summary(features_data)

        return features_data, summary, crs_name, warning
