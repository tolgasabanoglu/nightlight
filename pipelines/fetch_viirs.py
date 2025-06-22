import ee
import datetime
import requests
import tempfile
import numpy as np
import rasterio
from rasterio.transform import xy
import matplotlib.pyplot as plt
import pandas as pd
from geopy.geocoders import Nominatim

# 🌍 Authenticate and initialize Earth Engine
def init_ee(project="fetchviirs"):
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate(auth_mode="notebook")
        ee.Initialize(project=project)

# 📍 Convert a location to Earth Engine geometry with buffer
def location_to_geometry(location_name, buffer_km=50):
    geolocator = Nominatim(user_agent="nightlight-gee")
    loc = geolocator.geocode(location_name)
    if not loc:
        raise ValueError(f"❌ Could not geocode location: {location_name}")
    print(f"[📍] {location_name} → lat: {loc.latitude:.2f}, lon: {loc.longitude:.2f}")
    point = ee.Geometry.Point([loc.longitude, loc.latitude])
    return point.buffer(buffer_km * 1000).bounds()

# 📅 Load VIIRS monthly mean radiance
def load_viirs(location_name, year, month, project="fetchviirs"):
    init_ee(project)
    region = location_to_geometry(location_name)

    date_start = datetime.date(year, month, 1)
    date_end = datetime.date(year, month, 28)

    collection = (
        ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
        .filterDate(str(date_start), str(date_end))
    )

    if collection.size().getInfo() == 0:
        print(f"[⚠️] No monthly VIIRS data for {location_name} {year}-{month:02d}")
        return None, None

    image = collection.mean().clip(region)

    # Defensive: Check if 'avg_rad' band exists
    band_names = image.bandNames().getInfo()
    if not band_names or "avg_rad" not in band_names:
        print(f"[⚠️] No 'avg_rad' band found in {location_name} {year}-{month:02d}")
        return None, None

    image = image.select("avg_rad")

    url = image.getDownloadURL({
        "scale": 500,
        "region": region,
        "format": "GeoTIFF"
    })

    print(f"[⬇️] Downloading monthly composite: {year}-{month:02d}")
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=True) as tmpfile:
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            print(f"[❌] Download failed: {r.status_code}")
            print(r.text)
            return None, None

        with open(tmpfile.name, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

        with rasterio.open(tmpfile.name) as src:
            array = src.read(1)
            meta = src.meta.copy()

    print(f"[✅] Monthly VIIRS image loaded.")
    return array, meta

# 📆 Load VIIRS weekly mean from daily product
def load_viirs_weekly(location_name, year, month, week_number, project="fetchviirs"):
    init_ee(project)
    region = location_to_geometry(location_name)

    date_start = datetime.date(year, month, 1) + datetime.timedelta(days=(week_number - 1) * 7)
    date_end = date_start + datetime.timedelta(days=6)

    print(f"[📆] Weekly range: {date_start} → {date_end}")

    collection = (
        ee.ImageCollection("NOAA/VIIRS/001/VNP46A2")
        .filterDate(str(date_start), str(date_end))
        .select("DNB_BRDF_Corrected_NTL")
    )

    if collection.size().getInfo() == 0:
        print(f"[⚠️] No weekly VIIRS data for {location_name} {date_start} → {date_end}")
        return None, None

    image = collection.mean().clip(region)

    url = image.getDownloadURL({
        "scale": 500,
        "region": region,
        "format": "GeoTIFF"
    })

    print(f"[⬇️] Downloading weekly composite...")
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=True) as tmpfile:
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            print(f"[❌] Download failed: {r.status_code}")
            print(r.text)
            return None, None

        with open(tmpfile.name, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

        with rasterio.open(tmpfile.name) as src:
            array = src.read(1)
            meta = src.meta.copy()

    print(f"[✅] Weekly VIIRS image loaded.")
    return array, meta

# 🧾 Convert VIIRS raster to tidy DataFrame
def viirs_to_dataframe(array, meta, city, date_str):
    """Convert VIIRS raster to DataFrame with coordinates and radiance."""
    rows, cols = np.where(array > 0)
    xs, ys = xy(meta["transform"], rows, cols)

    return pd.DataFrame({
        "longitude": xs,
        "latitude": ys,
        "radiance": array[rows, cols],
        "city": city,
        "date": date_str
    })

# 🖼️ Plot VIIRS image
def plot_viirs(array, title="VIIRS Radiance"):
    plt.figure(figsize=(8, 6))
    vmax = np.nanpercentile(array, 98)
    plt.imshow(array, cmap="inferno", vmin=0, vmax=vmax)
    plt.title(title)
    plt.colorbar(label="Radiance (nW/cm²/sr)")
    plt.axis("off")
    plt.show()
