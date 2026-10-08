from typing import Dict, Any, Tuple, Optional
from shapely.geometry.base import BaseGeometry
from shapely.geometry import (
    Polygon, MultiPolygon,
    LineString, MultiLineString,
    Point, MultiPoint
)
from app.schemas.file_schema import MeasurementInfo, MeasurementSummary

class MeasurementService:
    @staticmethod
    def calculate_measurement(geom: Optional[BaseGeometry]) -> Tuple[str, MeasurementInfo]:
        """
        Calculates measurement for a single geometry already in a metric projected CRS.
        Returns:
            (geometry_type_string, MeasurementInfo)
        """
        if geom is None or geom.is_empty:
            return "Empty", MeasurementInfo(
                type=None,
                value=None,
                unit=None,
                message="Geometry is empty or null."
            )

        geom_type = geom.geom_type

        # Polygon and MultiPolygon: Area in m²
        if isinstance(geom, (Polygon, MultiPolygon)):
            area_val = round(float(geom.area), 2)
            return geom_type, MeasurementInfo(
                type="area",
                value=area_val,
                unit="m²",
                message=None
            )

        # LineString and MultiLineString: Length in m
        if isinstance(geom, (LineString, MultiLineString)):
            length_val = round(float(geom.length), 2)
            return geom_type, MeasurementInfo(
                type="length",
                value=length_val,
                unit="m",
                message=None
            )

        # Point and MultiPoint: No measurement
        if isinstance(geom, (Point, MultiPoint)):
            return geom_type, MeasurementInfo(
                type=None,
                value=None,
                unit=None,
                message=None
            )

        # Any other geometry (GeometryCollection, etc.)
        return geom_type, MeasurementInfo(
            type=None,
            value=None,
            unit=None,
            message="Measurement is not supported for this geometry type."
        )

    @staticmethod
    def aggregate_summary(feature_items: list[Dict[str, Any]]) -> MeasurementSummary:
        """
        Computes aggregate statistics across all features in a file.
        """
        polygon_count = 0
        line_count = 0
        point_count = 0
        unsupported_count = 0
        total_area = 0.0
        total_length = 0.0

        for feat in feature_items:
            geom_type = feat.get("geometry_type", "")
            measurement = feat.get("measurement", {})
            m_type = measurement.get("type")
            m_val = measurement.get("value")

            if geom_type in ("Polygon", "MultiPolygon"):
                polygon_count += 1
                if m_val is not None:
                    total_area += float(m_val)
            elif geom_type in ("LineString", "MultiLineString"):
                line_count += 1
                if m_val is not None:
                    total_length += float(m_val)
            elif geom_type in ("Point", "MultiPoint"):
                point_count += 1
            else:
                unsupported_count += 1

        return MeasurementSummary(
            total_features=len(feature_items),
            polygon_count=polygon_count,
            line_count=line_count,
            point_count=point_count,
            unsupported_count=unsupported_count,
            total_polygon_area_sqm=round(total_area, 2),
            total_line_length_m=round(total_length, 2)
        )
