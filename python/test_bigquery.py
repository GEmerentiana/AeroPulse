import os

from dotenv import load_dotenv
from google.cloud import bigquery


load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")
dataset_id = os.getenv("BIGQUERY_DATASET")
location = os.getenv("BIGQUERY_LOCATION", "EU")


if not project_id:
    raise ValueError("GCP_PROJECT_ID is missing from .env")

if not dataset_id:
    raise ValueError("BIGQUERY_DATASET is missing from .env")


print("Connecting to BigQuery...")
print(f"Project: {project_id}")
print(f"Dataset: {dataset_id}")
print(f"Location: {location}")


client = bigquery.Client(project=project_id)

print("BigQuery connection successful.")
print(f"Connected project: {client.project}")


query = """
SELECT
    CURRENT_DATE() AS today
"""


query_job = client.query(
    query,
    location=location
)

result = query_job.result()


for row in result:
    print(f"BigQuery date: {row.today}")


print("BigQuery test completed successfully.")