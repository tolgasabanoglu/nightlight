# 🛰️ Nightlight

A geospatial analysis project that uses VIIRS nighttime satellite imagery to track urban activity, infrastructure changes, and potential consumer signals around the world.

This project integrates satellite data with open infrastructure and environmental datasets to derive monthly insights — such as city brightness trends, blackout alerts, and possible economic patterns.

---

## 🔍 Project Goals

- Fetch and process VIIRS nightlight imagery by region and time
- Combine nightlight with OpenStreetMap (OSM), NDVI, and infrastructure layers
- Detect changes in brightness and surface activity near urban, commercial, or residential areas
- Generate consumer insights from geospatial changes
- Automate monthly reporting and updates

---

## 📁 Project Structure

nightlight/
├── notebooks/ # Exploration notebooks (e.g., Gaza blackout, NDVI overlay)
├── pipelines/ # Data pipeline scripts (e.g., fetch_viirs.py)
├── dbt/ # dbt models for transforming and analyzing data
├── gcp/ # GCP configs, cloud functions, and BigQuery setup
├── config/ # YAML and env config files
├── reports/ # Auto-generated markdown/HTML monthly insights
├── data/ # Local or temporary data files (GeoJSON, CSV)
├── utils/ # Utility functions for spatial ops, BigQuery, OSM, etc.
├── geodata/ # Static geospatial data modules (OSM roads, NDVI, etc.)
├── updaters/ # Scripts to refresh NDVI, OSM features, and footprints
├── consumer_insights/ # Core logic for consumer signals and region profiling
├── tests/ # Unit tests


---

## 🚀 How It Works

1. **Fetch VIIRS Data**  
   The `pipelines/fetch_viirs.py` script simulates downloading VIIRS brightness data. This will eventually pull from Earth Engine or NOAA sources.

2. **Integrate Other Layers**  
   The project combines:
   - OSM roads & retail zones
   - NDVI (vegetation) layers
   - Infrastructure footprints
   - Urban growth footprints (e.g., GHSL)

3. **Analyze Trends**  
   Scripts analyze brightness changes over time and relate them to:
   - Consumer activity near infrastructure
   - Changes in vegetation vs. brightness
   - Urban sprawl detection

4. **Generate Reports**  
   Monthly summaries are exported to `reports/`, e.g.:
   - `june_2025_trend_summary.md`
   - `consumer_insight_map.html`

---

## 💾 Requirements

- Python 3.9+
- [Google Cloud SDK](https://cloud.google.com/sdk) (for BigQuery)
- dbt (optional, for analytics models)

Install Python dependencies:
```bash
pip install -r requirements.txt

🛠 Example Usage

from pipelines.fetch_viirs import fetch_viirs_data

df = fetch_viirs_data("Gaza Strip", ("2024-01-01", "2024-03-01"))

📌 To Do / Roadmap

 Connect to real VIIRS API or Earth Engine
 Add blackout detection model
 Automate monthly pipeline (GCP Scheduler + Cloud Functions)
 Add consumer signal classifier
 Generate interactive reports

 📊 Example Use Cases

🛑 Blackout detection: Gaza, Ukraine, Sudan
🌆 Urban sprawl: Detect growth in new residential zones
🛍️ Consumer activity: Retail or commercial brightness changes
🚜 Land use shifts: NDVI vs. brightness in infrastructure zones
📉 Alert drops: Detect dimming in industrial or port areas

