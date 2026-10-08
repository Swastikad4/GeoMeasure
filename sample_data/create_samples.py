import os
import zipfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point, MultiPolygon

def generate_sample_files():
    out_dir = Path(__file__).parent.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. KML with Polygon (in Paris, France)
    poly = Polygon([
        (2.3522, 48.8566),
        (2.3550, 48.8566),
        (2.3550, 48.8590),
        (2.3522, 48.8590),
        (2.3522, 48.8566)
    ])
    gdf_poly = gpd.GeoDataFrame(
        [{"name": "Paris Parc A", "category": "Zone 1", "geometry": poly}],
        crs="EPSG:4326"
    )
    kml_poly_path = out_dir / "sample_polygon.kml"
    gdf_poly.to_file(str(kml_poly_path), driver="KML")

    # 2. KML with LineString and Point (in London)
    line = LineString([
        (-0.1278, 51.5074),
        (-0.1250, 51.5090),
        (-0.1200, 51.5080)
    ])
    point = Point(-0.1278, 51.5074)
    gdf_routes = gpd.GeoDataFrame(
        [
            {"name": "River Walk Route", "type": "Footpath", "geometry": line},
            {"name": "Meeting Point", "type": "Landmark", "geometry": point}
        ],
        crs="EPSG:4326"
    )
    kml_route_path = out_dir / "sample_routes.kml"
    gdf_routes.to_file(str(kml_route_path), driver="KML")

    # 3. Shapefile inside ZIP
    shp_temp_dir = out_dir / "_temp_shp"
    shp_temp_dir.mkdir(parents=True, exist_ok=True)
    
    poly1 = Polygon([(13.4050, 52.5200), (13.4100, 52.5200), (13.4100, 52.5240), (13.4050, 52.5240), (13.4050, 52.5200)])
    poly2 = Polygon([(13.4150, 52.5210), (13.4220, 52.5210), (13.4220, 52.5260), (13.4150, 52.5260), (13.4150, 52.5210)])

    gdf_shp = gpd.GeoDataFrame(
        [
            {"id_code": "PLG-01", "name": "Berlin Mitte Sector", "geometry": poly1},
            {"id_code": "PLG-02", "name": "Berlin Tiergarten East", "geometry": poly2}
        ],
        crs="EPSG:4326"
    )
    temp_shp_file = shp_temp_dir / "berlin_features.shp"
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
