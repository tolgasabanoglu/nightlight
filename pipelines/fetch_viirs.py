import ee
import geemap
import pandas as pd
from datetime import datetime, timedelta

# Initialize Earth Engine
ee.Initialize()

def fetch_viirs_from_gee(region_geojson, start_date, end_date, out_csv="data/fetched_viirs.csv"):
    """
    Fetch VIIRS DNB brightness for a given region and date range using Google Earth Engine.
    Args:
        region_geojson (dict): GeoJSON geometry of the region.
        start_date (str): Format "YYYY-MM-DD"
        end_date (str): Format "YYYY-MM-DD"
        out_csv (str): Path to output CSV file

    Returns:
        pd.DataFrame: Averaged brightness data per date
    """
    roi = ee.Geometry(region_geojson)

    # Load VIIRS DNB collection (VNP46A2 is daily)
    collection = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG") \
        .filterBounds(roi) \
        .filterDate(start_date, end_date)

    # List of images with average radiance over ROI
    def reduce_region(img):
        mean_dict = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=500,
            maxPixels=1e9
        )
        return ee.Feature(None, {
            "date": img.date().format("YYYY-MM-dd"),
            "brightness": mean_dict.get("avg_rad")
        })

    features = collection.map(reduce_region).getInfo()["features"]

    # Convert to DataFrame
    data = [{"date": f["properties"]["date"], "brightness": f["properties"]["brightness"]} for f in features]
    df = pd.DataFrame(data)

    df.to_csv(out_csv, index=False)
    print(f"✅ Saved to {out_csv}")
    return df
