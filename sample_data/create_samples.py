import os
import zipfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point, MultiPolygon

def generate_sample_files():
    out_dir = Path(__file__).parent.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. KML with Polygon (Central Vista & India Gate, New Delhi, India)
    poly = Polygon([
        (77.2100, 28.6100),
        (77.2350, 28.6100),
        (77.2350, 28.6250),
        (77.2100, 28.6250),
        (77.2100, 28.6100)
    ])
    gdf_poly = gpd.GeoDataFrame(
        [{"name": "Central Vista & India Gate Zone", "category": "New Delhi Heritage Zone", "geometry": poly}],
        crs="EPSG:4326"
    )
    kml_poly_path = out_dir / "sample_polygon.kml"
    gdf_poly.to_file(str(kml_poly_path), driver="KML")

    # 2. KML with LineString and Point (Marine Drive & Gateway of India, Mumbai, India)
    line = LineString([
        (72.8200, 18.9250),
        (72.8235, 18.9420),
        (72.8255, 18.9560),
        (72.8200, 18.9750)
    ])
    point = Point(72.8347, 18.9220)
    gdf_routes = gpd.GeoDataFrame(
        [
            {"name": "Mumbai Marine Drive Coastal Route", "type": "Coastal Transit", "geometry": line},
            {"name": "Gateway of India Landmark", "type": "Historic Monument", "geometry": point}
        ],
        crs="EPSG:4326"
    )
    kml_route_path = out_dir / "sample_routes.kml"
    gdf_routes.to_file(str(kml_route_path), driver="KML")

    # 3. Shapefile inside ZIP (Cubbon Park & Lalbagh, Bengaluru, Karnataka, India)
    shp_temp_dir = out_dir / "_temp_shp"
    shp_temp_dir.mkdir(parents=True, exist_ok=True)
    
    poly1 = Polygon([(77.5850, 12.9720), (77.5960, 12.9720), (77.5960, 12.9810), (77.5850, 12.9810), (77.5850, 12.9720)])
    poly2 = Polygon([(77.5830, 12.9460), (77.5920, 12.9460), (77.5920, 12.9550), (77.5830, 12.9550), (77.5830, 12.9460)])

    gdf_shp = gpd.GeoDataFrame(
        [
            {"id_code": "BLR-01", "name": "Bengaluru Cubbon Park Sector", "geometry": poly1},
            {"id_code": "BLR-02", "name": "Bengaluru Lalbagh Botanical Enclave", "geometry": poly2}
        ],
        crs="EPSG:4326"
    )
    temp_shp_file = shp_temp_dir / "india_bengaluru_parcels.shp"
    gdf_shp.to_file(str(temp_shp_file))

    zip_path = out_dir / "sample_shapefile.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in shp_temp_dir.iterdir():
            zf.write(f, arcname=f.name)

    # 4. Shapefile ZIP missing CRS (.prj file omitted)
    zip_no_prj_path = out_dir / "sample_missing_crs.zip"
    with zipfile.ZipFile(zip_no_prj_path, "w") as zf:
        for f in shp_temp_dir.iterdir():
            if f.suffix != ".prj":
                zf.write(f, arcname=f.name)

    # Clean up temp shp
    for f in shp_temp_dir.iterdir():
        f.unlink()
    shp_temp_dir.rmdir()

    # 5. Invalid / corrupt text file renamed as .kml
    corrupt_kml = out_dir / "sample_corrupt.kml"
    with open(corrupt_kml, "w") as f:
        f.write("THIS IS NOT A VALID KML OR XML FILE AT ALL")

    print(f"Sample geospatial files created in {out_dir}")

if __name__ == "__main__":
    generate_sample_files()
