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
# METRICS
# ============================================================

metrics = {
    "overall_rating": "over_all_rating",
    "seat_comfort": "seat_comfort",
    "cabin_staff_service": "cabin_staff_service",
    "food_beverages": "food__beverages",
    "inflight_entertainment": "inflight_entertainment",
    "ground_service": "ground_service",
    "wifi_connectivity": "wifi__connectivity",
    "value_for_money": "value_for_money",
}


# ============================================================
# CONVERT TO NUMERIC
# ============================================================

for column in metrics.values():
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# BUILD PRODUCTION DATASET
# ============================================================

results = []

for airline, group in df.groupby("aeropulse_airline_name"):

    total_reviews = len(group)

    row = {
        "airline_name": airline,
        "review_count": total_reviews,
    }

    for output_name, source_column in metrics.items():

        valid = group[source_column].notna().sum()

        average = group[source_column].mean()

        coverage = (
            valid / total_reviews * 100
            if total_reviews > 0
            else 0
        )

        row[f"{output_name}_rating"] = (
            round(average, 2)
            if pd.notna(average)
            else None
        )

        row[f"{output_name}_valid_reviews"] = int(valid)

        row[f"{output_name}_coverage_pct"] = round(
            coverage,
            2
        )

    results.append(row)


production = pd.DataFrame(results)


# ============================================================
# ADD EVIDENCE LEVEL
# ============================================================

production["evidence_level"] = production[
    "review_count"
].apply(
    lambda x:
        "Strong"
        if x >= 500
        else "Moderate"
        if x >= 100
        else "Limited"
)


# ============================================================
# SORT
# ============================================================

production = production.sort_values(
    by="review_count",
    ascending=False
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 70)
print("PASSENGER EXPERIENCE PRODUCTION DATASET")
print("=" * 70)

print(
    production.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    output_dir /
    "fact_passenger_experience_airline.csv"
)

production.to_csv(
    output_file,
    index=False
)


print()
print("=" * 70)
print("OUTPUT")
print("=" * 70)

print(output_file)

print()
print("Analysis complete.")