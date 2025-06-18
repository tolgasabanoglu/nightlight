import os
import pandas as pd
from datetime import datetime

def fetch_viirs_data(region, date_range, output_path="data/fetched_viirs.csv"):
    """
    Simulates fetching VIIRS nighttime lights data for a given region and date range.
    
    Args:
        region (str or dict): A region identifier or bounding box (lat/lon).
        date_range (tuple): Start and end date as ('YYYY-MM-DD', 'YYYY-MM-DD').
        output_path (str): Where to save the fetched data.
    
    Returns:
        pd.DataFrame: Simulated nightlight data.
    """
    start, end = [datetime.strptime(d, "%Y-%m-%d") for d in date_range]

    # Simulated time series data
    dates = pd.date_range(start=start, end=end, freq="7D")
    brightness = [round(20 + i*0.8, 2) for i in range(len(dates))]

    df = pd.DataFrame({
        "region": [region] * len(dates),
        "date": dates,
        "brightness": brightness
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved VIIRS data to {output_path}")
    return df
