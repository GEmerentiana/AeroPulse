import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery


# ---------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")
dataset_id = os.getenv("BIGQUERY_DATASET")
location = os.getenv("BIGQUERY_LOCATION", "EU")


# ---------------------------------------------------------
# 2. Validate environment variables
# ---------------------------------------------------------

if not project_id:
    raise ValueError("GCP_PROJECT_ID is missing from .env")

if not dataset_id:
    raise ValueError("BIGQUERY_DATASET is missing from .env")


# ---------------------------------------------------------
# 3. Define file and BigQuery table
# ---------------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

parquet_path = (
    project_root
    / "data"
    / "processed"
    / "opdi"
    / "aeropulse_flights.parquet"
)

table_id = f"{project_id}.{dataset_id}.staging_flights"


# ---------------------------------------------------------
# 4. Check that the Parquet file exists
# ---------------------------------------------------------

if not parquet_path.exists():
    raise FileNotFoundError(
        f"Parquet file not found: {parquet_path}"
    )


# ---------------------------------------------------------
# 5. Display configuration
# ---------------------------------------------------------

print("=" * 60)
print("AeroPulse - BigQuery Staging Loader")
print("=" * 60)

print(f"Project:       {project_id}")
print(f"Dataset:       {dataset_id}")
print(f"Location:      {location}")
print(f"Source file:   {parquet_path}")
print(f"Target table:  {table_id}")
print()


# ---------------------------------------------------------
# 6. Read the Parquet file
# ---------------------------------------------------------

print("Reading Parquet file...")

df = pd.read_parquet(parquet_path)

print(f"Rows loaded locally: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print()


# ---------------------------------------------------------
# 7. Display columns
# ---------------------------------------------------------

print("Columns:")
for column in df.columns:
    print(f"  - {column}")

print()


# ---------------------------------------------------------
# 8. Connect to BigQuery
# ---------------------------------------------------------

print("Connecting to BigQuery...")

client = bigquery.Client(project=project_id)

print("BigQuery connection successful.")
print()


# ---------------------------------------------------------
# 9. Configure BigQuery load job
# ---------------------------------------------------------

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)


# ---------------------------------------------------------
# 10. Upload DataFrame to BigQuery
# ---------------------------------------------------------

print("Uploading data to BigQuery...")
print("This may take a few minutes.")

load_job = client.load_table_from_dataframe(
    df,
    table_id,
    job_config=job_config,
    location=location,
)

load_job.result()


# ---------------------------------------------------------
# 11. Verify table
# ---------------------------------------------------------

table = client.get_table(table_id)

print()
print("=" * 60)
print("LOAD COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"BigQuery table: {table.full_table_id}")
print(f"Rows in table:  {table.num_rows:,}")
print(f"Columns:        {len(table.schema)}")
print()


# ---------------------------------------------------------
# 12. Compare local and BigQuery row counts
# ---------------------------------------------------------

local_rows = len(df)
bigquery_rows = table.num_rows

print("Row count reconciliation:")
print(f"Local Parquet rows:  {local_rows:,}")
print(f"BigQuery table rows: {bigquery_rows:,}")

if local_rows == bigquery_rows:
    print("STATUS: PASS - Row counts match.")
else:
    print("STATUS: FAIL - Row counts do not match.")
    raise ValueError(
        "Row count mismatch between Parquet and BigQuery."
    )


# ---------------------------------------------------------
# 13. Display BigQuery schema
# ---------------------------------------------------------

print()
print("BigQuery schema:")

for field in table.schema:
    print(
        f"  - {field.name}: "
        f"{field.field_type} "
        f"{field.mode}"
    )

print()
print("Staging table is ready for analysis.")