"""
GeoNexus: extract elevation and slope from SRTM DEM tiles.

Expected folders:
geonexus/
  myapp/
    process_dem.py
    ml_models/
      dem/
        N08E076.tif
        ...

Input:
C:\\Users\\GAYATHRI\\Downloads\\lanslide\\kerala_landslides_base.csv

Output:
C:\\Users\\GAYATHRI\\Downloads\\lanslide\\kerala_landslides_with_dem.csv

This script:
- reads the DEM tiles in windows (avoids loading the entire Kerala raster),
- calculates slope in degrees using metric pixel spacing,
- samples elevation and slope at each inventory point,
- leaves missing values as NaN (does not invent data).
"""

from pathlib import Path
import math
import sys
import warnings

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from rasterio.transform import rowcol
from rasterio.warp import transform as transform_coords
from rasterio.crs import CRS
from scipy.ndimage import gaussian_filter

# ----------------------- CONFIGURATION -----------------------

PROJECT_DIR = Path(r"C:\Users\GAYATHRI\PycharmProjects\geonexus")
DEM_DIR = PROJECT_DIR / "myapp" / "ml_models" / "dem"

INPUT_CSV = Path(
    r"C:\Users\GAYATHRI\Downloads\lanslide\kerala_landslides_base.csv"
)
OUTPUT_CSV = INPUT_CSV.parent / "kerala_landslides_with_dem.csv"

LAT_COL = "latitude"
LON_COL = "longitude"

# A 3x3 neighbourhood is enough for local slope at SRTM resolution.
# Tile data are in geographic coordinates; slope calculation below converts
# pixel dimensions approximately to metres based on each tile's latitude.
# ------------------------------------------------------------


def find_dem_tiles(folder: Path):
    """Return only source DEM tiles, excluding generated output rasters."""
    if not folder.exists():
        raise FileNotFoundError(
            f"DEM folder not found:\n{folder}\n"
            "Create this folder and copy all downloaded .tif tiles into it."
        )

    files = sorted(
        f for f in folder.glob("*.tif")
        if f.name.lower() not in {
            "kerala_dem_merged.tif",
            "kerala_slope_degrees.tif",
        }
        and not f.name.lower().endswith("_slope.tif")
    )
    if not files:
        raise FileNotFoundError(
            f"No .tif DEM tiles found in:\n{folder}"
        )
    return files


def validate_input(df: pd.DataFrame):
    required = {LAT_COL, LON_COL}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {sorted(missing)}\n"
            f"Available columns: {list(df.columns)}"
        )

    df[LAT_COL] = pd.to_numeric(df[LAT_COL], errors="coerce")
    df[LON_COL] = pd.to_numeric(df[LON_COL], errors="coerce")
    invalid = (
        df[LAT_COL].isna()
        | df[LON_COL].isna()
        | ~df[LAT_COL].between(-90, 90)
        | ~df[LON_COL].between(-180, 180)
    )
    if invalid.any():
        print(f"Warning: {int(invalid.sum())} rows have invalid coordinates.")
    return df


def read_tile_validity(src):
    """Return nodata-aware validity rules without loading the whole tile."""
    return src.nodata


def sample_elevation_and_slope(src, longitude, latitude):
    """
    Sample elevation and derive slope around the point.
    Uses a 3x3 neighbourhood and accounts for geographic pixel size in metres.
    """
    try:
        row, col = rowcol(src.transform, longitude, latitude)
    except Exception:
        return np.nan, np.nan

    if row < 1 or col < 1 or row >= src.height - 1 or col >= src.width - 1:
        # Still attempt elevation for points on the tile edge; slope needs 3x3.
        try:
            val = next(src.sample([(longitude, latitude)], masked=True))[0]
            elevation = float(val) if not np.ma.is_masked(val) and np.isfinite(val) else np.nan
        except Exception:
            elevation = np.nan
        return elevation, np.nan

    try:
        elev_arr = src.read(
            1,
            window=Window(col - 1, row - 1, 3, 3),
            masked=True,
        )
    except Exception:
        return np.nan, np.nan

    center = elev_arr[1, 1]
    if np.ma.is_masked(center) or not np.isfinite(float(center)):
        return np.nan, np.nan

    elevation = float(center)
    # Convert the masked integer raster to float BEFORE filling nodata with NaN.
    # Integer arrays (e.g. int16 SRTM) cannot represent NaN.
    arr = elev_arr.astype("float64").filled(np.nan)

    # If any cell is void/nodata, slope is not calculated for this point.
    if not np.isfinite(arr).all():
        return elevation, np.nan

    # For north-up geographic rasters, x pixel size is degrees longitude
    # and y pixel size is degrees latitude. Convert to approximate metres.
    xres_deg = abs(src.transform.a)
    yres_deg = abs(src.transform.e)
    lat_rad = math.radians(latitude)
    metres_per_degree_lat = 111132.0
    metres_per_degree_lon = max(1.0, 111320.0 * abs(math.cos(lat_rad)))
    dx = xres_deg * metres_per_degree_lon
    dy = yres_deg * metres_per_degree_lat

    if dx <= 0 or dy <= 0:
        return elevation, np.nan

    # Horn 3x3 slope algorithm (metres/metres).
    z1, z2, z3 = arr[0, 0], arr[0, 1], arr[0, 2]
    z4, z5, z6 = arr[1, 0], arr[1, 1], arr[1, 2]
    z7, z8, z9 = arr[2, 0], arr[2, 1], arr[2, 2]

    dzdx = ((z3 + 2.0 * z6 + z9) - (z1 + 2.0 * z4 + z7)) / (8.0 * dx)
    dzdy = ((z7 + 2.0 * z8 + z9) - (z1 + 2.0 * z2 + z3)) / (8.0 * dy)
    slope = math.degrees(math.atan(math.sqrt(dzdx * dzdx + dzdy * dzdy)))

    return elevation, slope


def main():
    print("=" * 64)
    print("GeoNexus - DEM Altitude and Slope Extraction")
    print("=" * 64)
    print(f"DEM folder : {DEM_DIR}")
    print(f"Input CSV  : {INPUT_CSV}")
    print(f"Output CSV : {OUTPUT_CSV}")

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found:\n{INPUT_CSV}")

    tiles = find_dem_tiles(DEM_DIR)
    print(f"\nFound {len(tiles)} DEM tile(s):")
    for tile in tiles:
        print(f"  - {tile.name}")

    df = pd.read_csv(INPUT_CSV)
    df = validate_input(df)
    print(f"\nLoaded {len(df):,} landslide records.")

    # Keep original coordinates as WGS84 longitude/latitude.
    # DEM coordinates are transformed per tile if its CRS differs.
    if "altitude" not in df.columns:
        df["altitude"] = np.nan
    else:
        df["altitude"] = pd.to_numeric(df["altitude"], errors="coerce")

    if "slope" not in df.columns:
        df["slope"] = np.nan
    else:
        df["slope"] = pd.to_numeric(df["slope"], errors="coerce")

    # Process each tile, sampling only points that fall within its bounds.
    # If tiles overlap at edges, first valid value wins.
    lon_values = df[LON_COL].to_numpy(dtype=float)
    lat_values = df[LAT_COL].to_numpy(dtype=float)
    alt_values = df["altitude"].to_numpy(dtype=float)
    slope_values = df["slope"].to_numpy(dtype=float)

    for tile_index, tile_path in enumerate(tiles, start=1):
        print(f"\n[{tile_index}/{len(tiles)}] Processing {tile_path.name} ...")
        try:
            with rasterio.open(tile_path) as src:
                if src.crs is None:
                    warnings.warn(f"Skipping tile with no CRS: {tile_path.name}")
                    continue

                # Use geographic coordinates for selecting likely rows first.
                # Transform all WGS84 points into the tile CRS for sampling.
                valid_coords = (
                    np.isfinite(lon_values)
                    & np.isfinite(lat_values)
                    & (np.isnan(alt_values) | np.isnan(slope_values))
                )
                indices = np.flatnonzero(valid_coords)
                if len(indices) == 0:
                    print("  All records already have altitude and slope.")
                    continue

                if src.crs == CRS.from_epsg(4326):
                    xs = lon_values[indices]
                    ys = lat_values[indices]
                else:
                    xs, ys = transform_coords(
                        CRS.from_epsg(4326),
                        src.crs,
                        lon_values[indices].tolist(),
                        lat_values[indices].tolist(),
                    )
                    xs = np.asarray(xs)
                    ys = np.asarray(ys)

                # Only points within tile bounds are candidates.
                left, bottom, right, top = src.bounds
                in_tile = (
                    (xs >= left) & (xs <= right)
                    & (ys >= bottom) & (ys <= top)
                )
                candidate_indices = indices[in_tile]
                candidate_xs = xs[in_tile]
                candidate_ys = ys[in_tile]

                print(f"  Candidate points in tile: {len(candidate_indices):,}")

                for i, x, y in zip(candidate_indices, candidate_xs, candidate_ys):
                    # Fill altitude/slope only if currently missing.
                    if np.isnan(alt_values[i]) or np.isnan(slope_values[i]):
                        elevation, slope = sample_elevation_and_slope(src, x, y)
                        if np.isnan(alt_values[i]) and np.isfinite(elevation):
                            alt_values[i] = elevation
                        if np.isnan(slope_values[i]) and np.isfinite(slope):
                            slope_values[i] = slope

        except rasterio.errors.RasterioError as exc:
            print(f"  ERROR reading {tile_path.name}: {exc}")
        except Exception as exc:
            print(f"  ERROR processing {tile_path.name}: {exc}")

    df["altitude"] = alt_values
    df["slope"] = slope_values

    # Keep output independent from the input; no fake values are filled.
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    total = len(df)
    missing_alt = int(df["altitude"].isna().sum())
    missing_slope = int(df["slope"].isna().sum())

    print("\n" + "=" * 64)
    print("PROCESSING COMPLETE")
    print("=" * 64)
    print(f"Total records          : {total:,}")
    print(f"Altitude found         : {total - missing_alt:,}")
    print(f"Altitude missing       : {missing_alt:,}")
    print(f"Slope found            : {total - missing_slope:,}")
    print(f"Slope missing          : {missing_slope:,}")
    print(f"\nOutput saved to:\n{OUTPUT_CSV}")

    if missing_alt or missing_slope:
        print(
            "\nNote: missing values can happen if coordinates fall outside the "
            "downloaded tiles, a tile has nodata, or a point lies on a tile edge."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nPROCESSING FAILED")
        print(f"{type(error).__name__}: {error}")
        sys.exit(1)
