from pathlib import Path
import pandas as pd


# ============================================================
# AeroPulse — Diagnose Europe Flag Mismatch
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "opdi"
    / "aeropulse_flights_enriched.parquet"
)


print("=" * 70)
print("AeroPulse — Europe Flag Diagnostic")
print("=" * 70)

print()
print("Loading enriched flight data...")

df = pd.read_parquet(INPUT_FILE)

print(f"Rows: {len(df):,}")
print()


# ============================================================
# 1. Departure continent values
# ============================================================

print("-" * 70)
print("1. DEPARTURE CONTINENT VALUES")
print("-" * 70)

print(
    df["departure_airport_continent"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# 2. Arrival continent values
# ============================================================

print()
print("-" * 70)
print("2. ARRIVAL CONTINENT VALUES")
print("-" * 70)

print(
    df["arrival_airport_continent"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# 3. Departure Europe flag values
# ============================================================

print()
print("-" * 70)
print("3. DEPARTURE EUROPE FLAG")
print("-" * 70)

print(
    df["departure_is_europe"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# 4. Arrival Europe flag values
# ============================================================

print()
print("-" * 70)
print("4. ARRIVAL EUROPE FLAG")
print("-" * 70)

print(
    df["arrival_is_europe"]
    .value_counts(dropna=False)
    .to_string()
)


# ============================================================
# 5. Cross-tab departure
# ============================================================

print()
print("-" * 70)
print("5. DEPARTURE CONTINENT vs EUROPE FLAG")
print("-" * 70)

departure_cross = pd.crosstab(
    df["departure_airport_continent"].fillna("NULL"),
    df["departure_is_europe"].fillna("NULL"),
    dropna=False
)

print(departure_cross.to_string())


# ============================================================
# 6. Cross-tab arrival
# ============================================================

print()
print("-" * 70)
print("6. ARRIVAL CONTINENT vs EUROPE FLAG")
print("-" * 70)

arrival_cross = pd.crosstab(
    df["arrival_airport_continent"].fillna("NULL"),
    df["arrival_is_europe"].fillna("NULL"),
    dropna=False
)

print(arrival_cross.to_string())


# ============================================================
# 7. Show mismatching departure rows
# ============================================================

print()
print("-" * 70)
print("7. DEPARTURE MISMATCH EXAMPLES")
print("-" * 70)

expected_departure = (
    df["departure_airport_continent"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("EUROPE")
)

actual_departure = (
    df["departure_is_europe"]
    .fillna(False)
    .astype(bool)
)

departure_mismatch = df[
    expected_departure != actual_departure
]

print(
    f"Departure mismatches: {len(departure_mismatch):,}"
)

if len(departure_mismatch) > 0:

    columns = [
        "departure_airport_icao",
        "departure_airport_reference_name",
        "departure_airport_country_code",
        "departure_airport_continent",
        "departure_is_europe",
    ]

    print()
    print(
        departure_mismatch[columns]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 8. Show mismatching arrival rows
# ============================================================

print()
print("-" * 70)
print("8. ARRIVAL MISMATCH EXAMPLES")
print("-" * 70)

expected_arrival = (
    df["arrival_airport_continent"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("EUROPE")
)

actual_arrival = (
    df["arrival_is_europe"]
    .fillna(False)
    .astype(bool)
)

arrival_mismatch = df[
    expected_arrival != actual_arrival
]

print(
    f"Arrival mismatches: {len(arrival_mismatch):,}"
)

if len(arrival_mismatch) > 0:

    columns = [
        "arrival_airport_icao",
        "arrival_airport_reference_name",
        "arrival_airport_country_code",
        "arrival_airport_continent",
        "arrival_is_europe",
    ]

    print()
    print(
        arrival_mismatch[columns]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# 9. Unique continent strings
# ============================================================

print()
print("-" * 70)
print("9. UNIQUE CONTINENT STRINGS")
print("-" * 70)

departure_values = sorted(
    df["departure_airport_continent"]
    .dropna()
    .astype(str)
    .unique()
)

arrival_values = sorted(
    df["arrival_airport_continent"]
    .dropna()
    .astype(str)
    .unique()
)

print("Departure:")
for value in departure_values:
    print(repr(value))

print()
print("Arrival:")
for value in arrival_values:
    print(repr(value))


# ============================================================
# 10. Summary
# ============================================================

print()
print("=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

print(
    f"Departure mismatches: {len(departure_mismatch):,}"
)

print(
    f"Arrival mismatches:   {len(arrival_mismatch):,}"
)

print()

if len(departure_mismatch) == 0 and len(arrival_mismatch) == 0:
    print("RESULT: Europe flags are logically consistent.")
else:
    print(
        "RESULT: Europe flag mismatch confirmed."
    )
    print(
        "The output above shows exactly which continent values "
        "are causing the mismatch."
    )

print("=" * 70)