
import geopandas as gpd
from pathlib import Path

# 1. Shapefile path
shp_path = Path(
    r"C:\Users\GAYATHRI\Downloads\lanslide\Kerela landslide.shp"
)

# 2. Load shapefile
gdf = gpd.read_file(shp_path)

print("Total records:", len(gdf))
print("Original CRS:", gdf.crs)
print("Geometry types:", gdf.geometry.geom_type.unique())
print("Available columns:", gdf.columns.tolist())

# 3. Convert to WGS84
if gdf.crs is None:
    raise ValueError(
        "CRS information missing. Check the .prj file."
    )

if gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# 4. Extract coordinates safely
# Works for Point geometry
if gdf.geometry.geom_type.eq("Point").all():
    gdf["longitude"] = gdf.geometry.x
    gdf["latitude"] = gdf.geometry.y
else:
    # For polygons or other geometries, use representative points
    points = gdf.geometry.representative_point()
    gdf["longitude"] = points.x
    gdf["latitude"] = points.y

# 5. Rename existing columns if present
rename_columns = {}

if "District" in gdf.columns:
    rename_columns["District"] = "district"

if "Type_of_sl" in gdf.columns:
    rename_columns["Type_of_sl"] = "landslide_type"

gdf = gdf.rename(columns=rename_columns)

# 6. Select only available columns
wanted_columns = [
    "latitude",
    "longitude",
    "district",
    "landslide_type",
    "Area",
    "LU_2018",
    "Reclass_Sl",
    "RASTERVALU"
]

available_columns = [
    col for col in wanted_columns
    if col in gdf.columns
]

result = gdf[available_columns].copy()

# 7. Save CSV without geometry
output_path = shp_path.parent / "kerala_landslides_base.csv"
result.to_csv(output_path, index=False)

print("\nCSV saved successfully!")
print("Output:", output_path)
print("\nAvailable output columns:")
print(result.columns.tolist())
print("\nFirst 5 records:")
print(result.head())
