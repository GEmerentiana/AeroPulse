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
# CREATE BUSINESS / LEISURE GROUP
# ============================================================

def classify_traveller(value):

    if value == "business":
        return "Business"

    if value in [
        "solo_leisure",
        "couple_leisure",
        "family_leisure"
    ]:
        return "Leisure"

    return "Unknown"


df["traveller_group"] = df[
    "type_of_traveller"
].apply(classify_traveller)


# ============================================================
# RATING COLUMNS
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
# CONVERT RATINGS TO NUMERIC
# ============================================================

for column in metrics.values():

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# CALCULATE AIRLINE × TRAVELLER GROUP
# ============================================================

results = []

for (airline, traveller_group), group in df.groupby(
    ["aeropulse_airline_name", "traveller_group"]
):

    row = {
        "airline_name": airline,
        "traveller_group": traveller_group,
        "review_count": len(group),
    }

    for output_name, source_column in metrics.items():

        valid = group[source_column].notna().sum()

        average = group[source_column].mean()

        row[f"{output_name}_rating"] = (
            round(average, 2)
            if pd.notna(average)
            else None
        )

        row[f"{output_name}_valid_reviews"] = int(valid)

    results.append(row)


traveller_metrics = pd.DataFrame(results)


# ============================================================
# SORT
# ============================================================

traveller_metrics = traveller_metrics.sort_values(
    by=[
        "airline_name",
        "traveller_group"
    ]
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 70)
print("BUSINESS VS LEISURE — PASSENGER EXPERIENCE")
print("=" * 70)

print(
    traveller_metrics.to_string(index=False)
)


# ============================================================
# SUMMARY BY TRAVELLER GROUP
# ============================================================

summary = []

for traveller_group, group in df.groupby(
    "traveller_group"
):

    row = {
        "traveller_group": traveller_group,
        "review_count": len(group),
    }

    for output_name, source_column in metrics.items():

        row[f"{output_name}_rating"] = round(
            group[source_column].mean(),
            2
        )

    summary.append(row)


summary_df = pd.DataFrame(summary)


print()
print("=" * 70)
print("TRAVELLER GROUP SUMMARY")
print("=" * 70)

print(
    summary_df.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    output_dir /
    "fact_passenger_experience_traveller.csv"
)

traveller_metrics.to_csv(
    output_file,
    index=False
)


summary_file = (
    output_dir /
    "passenger_experience_traveller_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


print()
print("=" * 70)
print("OUTPUT")
print("=" * 70)

print(output_file)
print(summary_file)

print()
print("Analysis complete.")