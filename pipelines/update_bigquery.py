# pipelines/update_bigquery.py

import pandas as pd
import os

def update_bigquery_from_csv(csv_path, table_name='nightlight_dataset.viirs_brightness'):
    """
    Mock function to simulate uploading data to BigQuery.

    Args:
        csv_path (str): Path to the processed CSV file
        table_name (str): BigQuery table name (project.dataset.table)

    Returns:
        int: Number of rows "uploaded"
    """
    if not os.path.exists(csv_path):
        print(f"[❌] File not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    print(f"[🛰️] Loaded {len(df)} rows from {csv_path}")
    
    # Simulate upload
    print(f"[🚀] Simulating upload to BigQuery table: {table_name}")
    
    # Later: use google-cloud-bigquery to push `df`
    # from google.cloud import bigquery
    # client = bigquery.Client()
    # job = client.load_table_from_dataframe(df, table_name, job_config=config)

    return len(df)

if __name__ == "__main__":
    # Example test run
    rows_uploaded = update_bigquery_from_csv("data/fetched_viirs.csv")
    print(f"[✅] Done. {rows_uploaded} rows would be uploaded.")
