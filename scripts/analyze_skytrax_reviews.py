import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# 1. File location
# ---------------------------------------------------------
file_path = Path(r"C:\Users\ray_k\Downloads\aviation-performance-recommendation\Skytrax Airline Review Data.xlsx")

# Change the path above if your file is somewhere else.
# ---------------------------------------------------------

print("Loading Skytrax dataset...")
df = pd.read_excel(file_path)

print("\n========================================")
print("SKYTRAX DATASET OVERVIEW")
print("========================================")

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
for col in df.columns:
    print(f" - {col}")

# ---------------------------------------------------------
# 2. Missing-value overview
# ---------------------------------------------------------

print("\n========================================")
print("MISSING VALUES")
print("========================================")

missing = (
    df.isna()
      .sum()
      .sort_values(ascending=False)
)

missing_pct = (
    df.isna()
      .mean()
      .mul(100)
      .round(2)
)

missing_report = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct
})

print(missing_report.to_string())

# ---------------------------------------------------------
# 3. Airline coverage
# ---------------------------------------------------------

print("\n========================================")
print("AIRLINE COVERAGE")
print("========================================")

airline_counts = (
    df["airline_name"]
    .value_counts()
    .reset_index()
)

airline_counts.columns = [
    "airline_name",
    "review_count"
]

print(f"Unique airlines: {df['airline_name'].nunique():,}")

print("\nTop 30 airlines by review count:")
print(
    airline_counts
    .head(30)
    .to_string(index=False)
)

# ---------------------------------------------------------
# 4. Traveller type
# ---------------------------------------------------------

print("\n========================================")
print("TRAVELLER TYPE")
print("========================================")

if "type_of_traveller" in df.columns:
    traveller_counts = (
        df["type_of_traveller"]
        .value_counts(dropna=False)
    )

    print(traveller_counts.to_string())

# ---------------------------------------------------------
# 5. Rating availability
# ---------------------------------------------------------

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

print("\n========================================")
print("RATING COVERAGE")
print("========================================")

rating_rows = []

for col in rating_columns:
    if col in df.columns:
        valid = df[col].notna().sum()
        pct = round(valid / len(df) * 100, 2)

        rating_rows.append({
            "field": col,
            "valid_reviews": valid,
            "coverage_pct": pct
        })

rating_report = pd.DataFrame(rating_rows)

print(rating_report.to_string(index=False))

# ---------------------------------------------------------
# 6. AeroPulse airline coverage
# ---------------------------------------------------------

aeropulse_airlines = [
    "Lufthansa",
    "Eurowings",
    "Ryanair",
    "easyJet",
    "British Airways",
    "Air France",
    "KLM",
    "Wizz Air",
    "Delta Air Lines",
    "Austrian Airlines",
    "SWISS",
    "Brussels Airlines",
    "Turkish Airlines",
    "Condor",
    "Finnair",
    "Aegean Airlines",
    "Vueling",
    "airBaltic",
    "SunExpress",
    "LOT Polish Airlines",
    "Aer Lingus",
    "TAP Air Portugal",
    "Pegasus Airlines",
    "SAS",
    "Air Nostrum",
    "KLM Cityhopper",
    "Air France HOP",
    "Eurowings Europe",
]

print("\n========================================")
print("AEROPULSE AIRLINE COVERAGE")
print("========================================")

dataset_airlines = set(
    df["airline_name"]
    .dropna()
    .astype(str)
    .str.strip()
)

for airline in aeropulse_airlines:
    matches = [
        x for x in dataset_airlines
        if airline.lower() in x.lower()
        or x.lower() in airline.lower()
    ]

    print(f"\n{airline}")
    print(f"  Possible dataset matches: {matches}")

# ---------------------------------------------------------
# 7. Save reports
# ---------------------------------------------------------

output_dir = Path("data/passenger_experience")
output_dir.mkdir(parents=True, exist_ok=True)

airline_counts.to_csv(
    output_dir / "skytrax_airline_review_counts.csv",
    index=False
)

rating_report.to_csv(
    output_dir / "skytrax_rating_coverage.csv",
    index=False
)

print("\n========================================")
print("REPORTS SAVED")
print("========================================")

print(output_dir / "skytrax_airline_review_counts.csv")
print(output_dir / "skytrax_rating_coverage.csv")

print("\nAnalysis complete.")