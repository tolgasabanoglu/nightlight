import ee
import datetime
import requests
import rasterio
import numpy as np
import tempfile
from geopy.geocoders import Nominatim

def init_ee(project="fetchviirs"):
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate(auth_mode='notebook')
        ee.Initialize(project=project)

def location_to_geometry(location_name, buffer_km=50):
    geolocator = Nominatim(user_agent="nightlight-gee")
    loc = geolocator.geocode(location_name)
    if not loc:
        raise ValueError(f"Could not geocode location: {location_name}")
    point = ee.Geometry.Point([loc.longitude, loc.latitude])
    region = point.buffer(buffer_km * 1000).bounds()
    return region

def load_viirs(location_name, year, month, project="fetchviirs"):
    init_ee(project)
    region = location_to_geometry(location_name)

    date_start = datetime.date(year, month, 1)
    date_end = datetime.date(year, month, 28)

    image = (
        ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
        .filterDate(str(date_start), str(date_end))
        .mean()
        .select("avg_rad")
        .clip(region)
    )

    url = image.getDownloadURL({
        "scale": 500,
        "region": region,
        "format": "GeoTIFF"
    })

    print(f"[⬇️] Loading image from: {url}")
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=True) as tmpfile:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(tmpfile.name, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)
            with rasterio.open(tmpfile.name) as src:
                array = src.read(1)
                meta = src.meta.copy()
            print(f"[✅] Loaded image into memory.")
            return array, meta
        else:
            print(f"[❌] Download failed: {r.status_code}")
            print(r.text)
            return None, None
