from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

file_path = Path(
    r"C:\Users\ray_k\Downloads\aviation-performance-recommendation\Skytrax Airline Review Data.xlsx"
)

mapping_path = Path(
    r"data\passenger_experience\skytrax_airline_mapping.csv"
)

output_dir = Path(r"data\passenger_experience")
output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading Skytrax dataset...")

df = pd.read_excel(file_path)
mapping = pd.read_csv(mapping_path)


# ============================================================
# APPLY VERIFIED AIRLINE MAPPING
# ============================================================

df = df.merge(
    mapping,
    left_on="airline_name",
    right_on="skytrax_airline_name",
    how="inner"
)

print()
print("=" * 50)
print("VERIFIED PASSENGER EXPERIENCE DATA")
print("=" * 50)

print(f"Rows after airline mapping: {len(df):,}")
print(f"Airlines: {df['aeropulse_airline_name'].nunique()}")


# ============================================================
# RATING COLUMNS
# ============================================================

rating_columns = [
    "over_all_rating",
    "seat_comfort",
    "cabin_staff_service",
    "food__beverages",
    "inflight_entertainment",
    "ground_service",
    "wifi__connectivity",
    "value_for_money",
]


# ============================================================
# CONVERT RATINGS TO NUMERIC
# ============================================================

for column in rating_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# AIRLINE-LEVEL METRICS
# ============================================================

results = []

for airline, group in df.groupby("aeropulse_airline_name"):

    row = {
        "airline_name": airline,
        "review_count": len(group),
    }

    for column in rating_columns:
        row[column] = group[column].mean()

    results.append(row)


airline_metrics = pd.DataFrame(results)


# ============================================================
# ROUND METRICS
# ============================================================

for column in rating_columns:
    airline_metrics[column] = airline_metrics[column].round(2)


# ============================================================
# SORT
# ============================================================

airline_metrics = airline_metrics.sort_values(
    by="review_count",
    ascending=False
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 50)
print("AIRLINE PASSENGER EXPERIENCE METRICS")
print("=" * 50)

print(
    airline_metrics.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    output_dir /
    "skytrax_airline_passenger_experience.csv"
)

airline_metrics.to_csv(
    output_file,
    index=False
)

print()
print("=" * 50)
print("OUTPUT")
print("=" * 50)

print(output_file)

print()
print("Analysis complete.")