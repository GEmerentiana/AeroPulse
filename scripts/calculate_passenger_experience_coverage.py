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
# CALCULATE AIRLINE × METRIC COVERAGE
# ============================================================

results = []

for airline, group in df.groupby("aeropulse_airline_name"):

    total_reviews = len(group)

    for metric in rating_columns:

        valid_reviews = group[metric].notna().sum()

        coverage_pct = (
            valid_reviews / total_reviews * 100
            if total_reviews > 0
            else 0
        )

        results.append({
            "airline_name": airline,
            "metric": metric,
            "total_reviews": total_reviews,
            "valid_reviews": valid_reviews,
            "coverage_pct": round(coverage_pct, 2),
        })


coverage = pd.DataFrame(results)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 70)
print("AIRLINE × METRIC COVERAGE")
print("=" * 70)

print(
    coverage.to_string(index=False)
)


# ============================================================
# SAVE LONG-FORM TABLE
# ============================================================

long_file = (
    output_dir /
    "skytrax_airline_metric_coverage.csv"
)

coverage.to_csv(
    long_file,
    index=False
)


# ============================================================
# CREATE WIDE COVERAGE TABLE
# ============================================================

wide = coverage.pivot(
    index="airline_name",
    columns="metric",
    values="coverage_pct"
).reset_index()


wide_file = (
    output_dir /
    "skytrax_airline_metric_coverage_wide.csv"
)

wide.to_csv(
    wide_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("OUTPUT")
print("=" * 70)

print(long_file)
print(wide_file)

print()
print("Analysis complete.")