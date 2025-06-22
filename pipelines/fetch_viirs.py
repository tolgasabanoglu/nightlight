import os
import math
import requests
from pathlib import Path
from datetime import datetime
from geopy.geocoders import Nominatim


def location_to_tile(lat, lon):
    """Convert lat/lon to VIIRS tile name, like 30N030E."""
    lat_deg = int(math.floor(lat / 10.0) * 10)
    lon_deg = int(math.floor(lon / 10.0) * 10)

    lat_str = f"{abs(lat_deg):02d}{'N' if lat_deg >= 0 else 'S'}"
    lon_str = f"{abs(lon_deg):03d}{'E' if lon_deg >= 0 else 'W'}"
    return f"{lat_str}{lon_str}"


def fetch_viirs_tif(year: int, month: int, tile: str = "30N030E", product: str = "vcmcfg"):
    """
    Download VIIRS GeoTIFF (.tif) from NOAA EOG monthly composites.

    Args:
        year (int)
        month (int)
        tile (str): Tile code like '30N030E'
        product (str): One of 'vcmcfg', 'vcm', 'vcm-orm'

    Returns:
        Path or None
    """
    month_str = str(month).zfill(2)
    base_url = f"https://eogdata.mines.edu/nighttime_light/monthly/v10/{year}{month_str}/{product}/"

    filename = (
        f"SVDNB_npp_{year}{month_str}01-{year}{month_str}31_{tile}_"
        f"{product}_v10_c{year}{month_str}151200.avg_rade9.tif"
    )

    out_dir = Path("/Users/tolgasabanoglu/Desktop/github/nightlight/data/viirs_tif")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    url = base_url + filename
    print(f"[⬇️] Fetching {url}...")

    r = requests.get(url, stream=True)

    if r.status_code == 200:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[✅] Saved to: {out_path}")
        return out_path
    else:
        print(f"[⚠️] Failed: {r.status_code} — {url}")
        return None


def fetch_viirs_tif_by_location(location: str, year: int, month: int, product: str = "vcmcfg"):
    """
    Geocode a place name → download matching VIIRS .tif for that tile.

    Args:
        location (str): e.g. "Gaza Strip", "Istanbul", "Hanoi"
        year (int)
        month (int)
        product (str): 'vcmcfg', 'vcm', etc.

    Returns:
        Path or None
    """
    geolocator = Nominatim(user_agent="nightlight-project")
    loc = geolocator.geocode(location)

    if not loc:
        print(f"[❌] Location not found: {location}")
        return None

    tile = location_to_tile(loc.latitude, loc.longitude)
    print(f"[📍] {location} → Tile: {tile} (lat: {loc.latitude:.2f}, lon: {loc.longitude:.2f})")

    return fetch_viirs_tif(year, month, tile=tile, product=product)