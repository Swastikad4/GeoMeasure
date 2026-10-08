import logging
from typing import Tuple, Optional
import geopandas as gpd
from pyproj import CRS

logger = logging.getLogger(__name__)

class CRSService:
    @staticmethod
    def detect_and_normalize_crs(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, Optional[str], Optional[str]]:
        """
        Detects the CRS of the GeoDataFrame.
        Returns:
            (gdf_with_crs, crs_name, warning_message)
        """
        warning: Optional[str] = None
        
        if gdf.crs is None:
            warning = "Warning: The uploaded file is missing CRS definition. Assumed EPSG:4326 (WGS 84); measurement accuracy may be affected."
            gdf = gdf.set_crs("EPSG:4326", allow_override=True)
            crs_name = "EPSG:4326 (Assumed - Missing in file)"
            return gdf, crs_name, warning

        try:
            crs_obj = CRS.from_user_input(gdf.crs)
            if crs_obj.to_epsg():
                crs_name = f"EPSG:{crs_obj.to_epsg()}"
            else:
                crs_name = crs_obj.name or str(gdf.crs)
        except Exception:
            crs_name = str(gdf.crs)

        return gdf, crs_name, warning

    @staticmethod
    def transform_to_projected_for_measurement(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, str]:
        """
        Ensures the GeoDataFrame is in an appropriate metric projected CRS.
        If geographic (degrees e.g. EPSG:4326), estimates an optimal UTM projection.
        Returns:
            (projected_gdf, projected_crs_name)
        """
        if gdf.empty or gdf.geometry.isnull().all():
            return gdf, "None"

        # Filter out empty or null geometries for CRS estimation
        valid_geoms = gdf[gdf.geometry.notnull() & (~gdf.geometry.is_empty)]
        if valid_geoms.empty:
            return gdf, "None"

        current_crs = gdf.crs
        if current_crs is None:
            gdf = gdf.set_crs("EPSG:4326", allow_override=True)
            valid_geoms = valid_geoms.set_crs("EPSG:4326", allow_override=True)

        is_geographic = False
        try:
            crs_obj = CRS.from_user_input(gdf.crs)
            is_geographic = crs_obj.is_geographic
        except Exception:
            is_geographic = True

        if is_geographic:
            try:
                # Estimate optimal UTM projection based on centroid of valid features
                utm_crs = valid_geoms.estimate_utm_crs()
                if utm_crs:
                    projected_gdf = gdf.to_crs(utm_crs)
                    return projected_gdf, f"{utm_crs.to_string()} (Auto UTM Projection)"
            except Exception as e:
                logger.warning(f"Could not estimate UTM projection: {e}. Falling back to World Equal Area EPSG:6933.")
            
            # Fallback for global or wide spans: EPSG:6933 (Equal Earth / cylindrical equal area)
            try:
                projected_gdf = gdf.to_crs("EPSG:6933")
                return projected_gdf, "EPSG:6933 (World Equal Area Cylindrical)"
            except Exception:
                # Fallback to pseudo-mercator if all else fails
                projected_gdf = gdf.to_crs("EPSG:3857")
                return projected_gdf, "EPSG:3857 (Projected)"

        # Already projected
        return gdf, str(gdf.crs)
