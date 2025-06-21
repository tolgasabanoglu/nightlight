import os
import requests
import datetime
from pathlib import Path

# Load Earthdata credentials from environment variables
NASA_USERNAME = os.getenv("EARTHDATA_USER")
NASA_PASSWORD = os.getenv("EARTHDATA_PASS")


def fetch_viirs_data(region, date_range, mode="real"):
    """
    Main interface to fetch VIIRS data, either real or mock.

    Args:
        region (str): Name of the region (currently unused in real mode)
        date_range (tuple): ("YYYY-MM-DD", "YYYY-MM-DD")
        mode (str): "real" or "mock"

    Returns:
        list: Downloaded file paths (real) or mock DataFrame (mock)
    """
    if mode == "real":
        return fetch_real_viirs_data(region, date_range)
    elif mode == "mock":
        return fetch_mock_viirs_data(region, date_range)
    else:
        raise ValueError("Invalid mode. Use 'real' or 'mock'")


def fetch_real_viirs_data(region, date_range):
    """
    Downloads VIIRS VNP46A2 HDF files from NASA LAADS archive.

    Args:
        region (str): Region name (currently unused)
        date_range (tuple): Start and end date in YYYY-MM-DD

    Returns:
        list: Paths to downloaded files
    """
    start, end = date_range
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    out_dir = Path("data/viirs_raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A2"
    tile = "h21v05"  # Placeholder: update later to match real region/tile coverage

    downloaded = []

    for single_date in daterange(start_date, end_date):
        year = single_date.year
        doy = single_date.timetuple().tm_yday
        date_folder = f"{year}.{str(doy).zfill(3)}"

        filename = f"VNP46A2.A{single_date.strftime('%Y%m%d')}.{tile}.001.h5"
        file_url = f"{base_url}/{date_folder}/{filename}"
        dest = out_dir / filename

        print(f"[⬇️] Fetching {file_url}...")

        response = requests.get(file_url, auth=(NASA_USERNAME, NASA_PASSWORD), stream=True)

        if response.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            print(f"[✅] Downloaded to: {dest}")
            downloaded.append(str(dest))
        else:
            print(f"[⚠️] Failed to download: {file_url} (Status {response.status_code})")

    return downloaded


def fetch_mock_viirs_data(region, date_range):
    """
    Generates fake VIIRS brightness values (for testing only).

    Args:
        region (str): Name of the region
        date_range (tuple): ("YYYY-MM-DD", "YYYY-MM-DD")

    Returns:
        pd.DataFrame: Simulated nightlight data
    """
    import pandas as pd

    start, end = date_range
    dates = pd.date_range(start=start, end=end, freq="7D")
    brightness = [round(20 + i * 0.8, 2) for i in range(len(dates))]

    df = pd.DataFrame({
        "region": [region] * len(dates),
        "date": dates,
        "brightness": brightness
    })

    df.to_csv("data/fetched_viirs.csv", index=False)
    print("✅ Saved VIIRS data to data/fetched_viirs.csv")
    return df


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + datetime.timedelta(n)
