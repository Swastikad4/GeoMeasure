from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str

class MeasurementInfo(BaseModel):
    type: Optional[str] = None  # "area", "length", or None
    value: Optional[float] = None
    unit: Optional[str] = None  # "m²", "m", or None
    message: Optional[str] = None

class FeatureInfo(BaseModel):
    feature_id: int
    geometry_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    measurement: MeasurementInfo
    geometry_geojson: Optional[Dict[str, Any]] = None

class MeasurementSummary(BaseModel):
    total_features: int = 0
    polygon_count: int = 0
    line_count: int = 0
    point_count: int = 0
    unsupported_count: int = 0
    total_polygon_area_sqm: float = 0.0
    total_line_length_m: float = 0.0

class FileDetail(BaseModel):
    id: str
    filename: str
    file_type: str
    file_path: Optional[str] = None
    feature_count: int
    crs: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    created_at: str
    summary: Optional[MeasurementSummary] = None

class FeatureCollectionResponse(BaseModel):
    file_id: str
    crs: Optional[str] = None
    feature_count: int
    features: List[FeatureInfo]

class MeasurementListResponse(BaseModel):
    file_id: str
    crs: Optional[str] = None
    summary: MeasurementSummary
    measurements: List[Dict[str, Any]]
