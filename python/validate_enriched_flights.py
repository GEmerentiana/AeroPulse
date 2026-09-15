from pathlib import Path
import pandas as pd


# ============================================================
# AeroPulse — Validate Enriched OPDI Flight Data
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "opdi"
    / "aeropulse_flights_enriched.parquet"
)

REPORT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "opdi"
    / "enriched_validation_report.csv"
)


# ============================================================
# Expected columns
# ============================================================

BASE_COLUMNS = [
    "source",
    "source_version",
    "flight_id",
    "icao24",
    "callsign",
    "flight_date",
    "departure_airport_icao",
    "arrival_airport_icao",
    "departure_airport_iata",
    "arrival_airport_iata",
    "departure_airport_name",
    "arrival_airport_name",
    "departure_country",
    "arrival_country",
    "icao_operator",
    "airline_name",
    "airline_category",
    "airline_identification_status",
    "registration",
    "aircraft_model",
    "aircraft_typecode",
    "aircraft_class",
    "first_seen",
    "last_seen",
    "observation_duration_minutes",
    "route_icao",
    "route_iata",
    "route_direction",
    "target_airport_role",
    "is_target_airport_departure",
    "is_target_airport_arrival",
    "has_known_departure",
    "has_known_arrival",
    "has_known_operator",
    "has_known_callsign",
    "has_complete_route",
    "is_target_airline",
    "data_quality_status",
]

ENRICHMENT_COLUMNS = [
    "departure_airport_reference_name",
    "departure_airport_reference_iata",
    "departure_airport_country_code",
    "departure_airport_continent",
    "departure_airport_geographic_scope",
    "departure_airport_latitude",
    "departure_airport_longitude",
    "departure_airport_municipality",
    "arrival_airport_reference_name",
    "arrival_airport_reference_iata",
    "arrival_airport_country_code",
    "arrival_airport_continent",
    "arrival_airport_geographic_scope",
    "arrival_airport_latitude",
    "arrival_airport_longitude",
    "arrival_airport_municipality",
    "network_geographic_scope",
    "departure_is_germany",
    "arrival_is_germany",
    "departure_is_europe",
    "arrival_is_europe",
    "both_endpoints_in_europe",
    "airport_reference_complete",
]

EXPECTED_COLUMNS = BASE_COLUMNS + ENRICHMENT_COLUMNS


# ============================================================
# Target airports
# ============================================================

TARGET_AIRPORTS = {
    "EDDF": "FRA",
    "EDDM": "MUC",
    "EDDB": "BER",
    "EDDL": "DUS",
    "EDDH": "HAM",
}


# ============================================================
# Target airlines
# ============================================================

TARGET_AIRLINES = {
    "DLH": "Lufthansa",
    "AFR": "Air France",
    "KLM": "KLM",
    "BAW": "British Airways",
    "RYR": "Ryanair",
    "EZY": "easyJet",
    "WZZ": "Wizz Air",
    "EWG": "Eurowings",
}


EXPECTED_AIRLINE_CATEGORIES = {
    "DLH": "Legacy",
    "AFR": "Legacy",
    "KLM": "Legacy",
    "BAW": "Legacy",
    "RYR": "Low-cost",
    "EZY": "Low-cost",
    "WZZ": "Low-cost",
    "EWG": "Low-cost",
}


# ============================================================
# Validation results
# ============================================================

results = []


def record(test_name, status, details):
    results.append(
        {
            "test": test_name,
            "status": status,
            "details": details,
        }
    )

    if status == "PASS":
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")

    print(f"       {details}")


# ============================================================
# Start
# ============================================================

print("=" * 70)
print("AeroPulse — Enriched Flight Data Validation")
print("=" * 70)

print()
print("Input file:")
print(INPUT_FILE)


# ============================================================
# Check input file
# ============================================================

if not INPUT_FILE.exists():

    print()
    print("ERROR: Input file does not exist.")
    print()
    print("Expected:")
    print(INPUT_FILE)
    print()
    print("Run enrich_opdi_airports.py first.")

    raise SystemExit(1)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading enriched flight data...")

df = pd.read_parquet(INPUT_FILE)

print(f"Rows loaded:    {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# ============================================================
# 1. Column validation
# ============================================================

print()
print("-" * 70)
print("1. COLUMN VALIDATION")
print("-" * 70)

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in df.columns
]

unexpected_columns = [
    column
    for column in df.columns
    if column not in EXPECTED_COLUMNS
]

if not missing_columns and not unexpected_columns:

    record(
        "Expected schema",
        "PASS",
        f"All {len(EXPECTED_COLUMNS)} expected columns present; "
        "no unexpected columns."
    )

else:

    details = []

    if missing_columns:
        details.append(
            "Missing: " + ", ".join(missing_columns)
        )

    if unexpected_columns:
        details.append(
            "Unexpected: " + ", ".join(unexpected_columns)
        )

    record(
        "Expected schema",
        "FAIL",
        " | ".join(details)
    )


# ============================================================
# 2. Row count
# ============================================================

print()
print("-" * 70)
print("2. ROW COUNT")
print("-" * 70)

if len(df) > 0:

    record(
        "Rows exist",
        "PASS",
        f"{len(df):,} enriched flight records found."
    )

else:

    record(
        "Rows exist",
        "FAIL",
        "Dataset contains zero rows."
    )


# ============================================================
# 3. Flight date validation
# ============================================================

print()
print("-" * 70)
print("3. FLIGHT DATE VALIDATION")
print("-" * 70)

df["flight_date"] = pd.to_datetime(
    df["flight_date"],
    errors="coerce"
)

invalid_dates = int(
    df["flight_date"].isna().sum()
)

if invalid_dates == 0:

    record(
        "Valid flight dates",
        "PASS",
        "No invalid or missing flight dates."
    )

else:

    record(
        "Valid flight dates",
        "FAIL",
        f"{invalid_dates:,} invalid or missing flight dates."
    )


min_date = df["flight_date"].min()
max_date = df["flight_date"].max()

print()
print(f"Minimum flight date: {min_date.date()}")
print(f"Maximum flight date: {max_date.date()}")


# ============================================================
# 4. 12-month coverage
# ============================================================

print()
print("-" * 70)
print("4. 12-MONTH COVERAGE")
print("-" * 70)

expected_months = pd.period_range(
    start="2025-08",
    end="2026-07",
    freq="M"
)

actual_months = sorted(
    df["flight_date"]
    .dt.to_period("M")
    .dropna()
    .unique()
)

missing_months = [
    str(month)
    for month in expected_months
    if month not in actual_months
]

if not missing_months:

    record(
        "All 12 months present",
        "PASS",
        "August 2025 through July 2026 are all represented."
    )

else:

    record(
        "All 12 months present",
        "FAIL",
        "Missing months: " + ", ".join(missing_months)
    )


# ============================================================
# 5. Date range
# ============================================================

print()
print("-" * 70)
print("5. DATE RANGE")
print("-" * 70)

expected_start = pd.Timestamp("2025-08-01")
expected_end = pd.Timestamp("2026-07-31")

outside_range = (
    (df["flight_date"] < expected_start)
    |
    (df["flight_date"] > expected_end)
)

outside_count = int(
    outside_range.sum()
)

if outside_count == 0:

    record(
        "Records inside 12-month window",
        "PASS",
        "All records are between 2025-08-01 and 2026-07-31."
    )

else:

    record(
        "Records inside 12-month window",
        "FAIL",
        f"{outside_count:,} records fall outside the expected window."
    )


# ============================================================
# 6. Duplicate flight IDs
# ============================================================

print()
print("-" * 70)
print("6. DUPLICATE CHECK")
print("-" * 70)

duplicate_count = int(
    df["flight_id"].duplicated().sum()
)

if duplicate_count == 0:

    record(
        "Duplicate flight IDs",
        "PASS",
        "No duplicate flight IDs found."
    )

else:

    record(
        "Duplicate flight IDs",
        "FAIL",
        f"{duplicate_count:,} duplicate flight IDs found."
    )


# ============================================================
# 7. Target airports
# ============================================================

print()
print("-" * 70)
print("7. TARGET AIRPORT VALIDATION")
print("-" * 70)

airport_values = set()

airport_values.update(
    df["departure_airport_icao"]
    .dropna()
    .astype(str)
    .unique()
)

airport_values.update(
    df["arrival_airport_icao"]
    .dropna()
    .astype(str)
    .unique()
)

missing_airports = [
    f"{icao} ({iata})"
    for icao, iata in TARGET_AIRPORTS.items()
    if icao not in airport_values
]

if not missing_airports:

    record(
        "All target airports present",
        "PASS",
        "FRA, MUC, BER, DUS and HAM are represented."
    )

else:

    record(
        "All target airports present",
        "FAIL",
        "Missing: " + ", ".join(missing_airports)
    )


# ============================================================
# 8. Target airlines
# ============================================================

print()
print("-" * 70)
print("8. TARGET AIRLINE VALIDATION")
print("-" * 70)

operator_values = set(
    df["icao_operator"]
    .dropna()
    .astype(str)
    .unique()
)

missing_airlines = [
    f"{code} ({name})"
    for code, name in TARGET_AIRLINES.items()
    if code not in operator_values
]

if not missing_airlines:

    record(
        "All target airlines present",
        "PASS",
        "All 8 target airline operator codes are represented."
    )

else:

    record(
        "All target airlines present",
        "FAIL",
        "Missing: " + ", ".join(missing_airlines)
    )


# ============================================================
# 9. Airline mapping consistency
# ============================================================

print()
print("-" * 70)
print("9. AIRLINE MAPPING")
print("-" * 70)

mapping_failures = []

for operator_code, expected_name in TARGET_AIRLINES.items():

    subset = df[
        df["icao_operator"].astype(str) == operator_code
    ]

    if subset.empty:
        continue

    actual_names = sorted(
        subset["airline_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if actual_names != [expected_name]:

        mapping_failures.append(
            f"{operator_code}: expected {expected_name}, "
            f"found {actual_names}"
        )


if not mapping_failures:

    record(
        "Target airline mapping",
        "PASS",
        "Each target operator maps consistently to the intended airline name."
    )

else:

    record(
        "Target airline mapping",
        "FAIL",
        " | ".join(mapping_failures)
    )


# ============================================================
# 10. Airline category consistency
# ============================================================

print()
print("-" * 70)
print("10. AIRLINE CATEGORY")
print("-" * 70)

category_failures = []

for operator_code, expected_category in EXPECTED_AIRLINE_CATEGORIES.items():

    subset = df[
        df["icao_operator"].astype(str) == operator_code
    ]

    if subset.empty:
        continue

    actual_categories = sorted(
        subset["airline_category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if actual_categories != [expected_category]:

        category_failures.append(
            f"{operator_code}: expected {expected_category}, "
            f"found {actual_categories}"
        )


if not category_failures:

    record(
        "Airline categories",
        "PASS",
        "Legacy and Low-cost classifications are consistent."
    )

else:

    record(
        "Airline categories",
        "FAIL",
        " | ".join(category_failures)
    )


# ============================================================
# 11. Airport reference completeness
# ============================================================

print()
print("-" * 70)
print("11. AIRPORT REFERENCE COMPLETENESS")
print("-" * 70)

reference_complete_count = int(
    df["airport_reference_complete"]
    .fillna(False)
    .sum()
)

reference_complete_pct = (
    reference_complete_count / len(df) * 100
    if len(df) > 0
    else 0
)

print(
    f"Complete airport reference: "
    f"{reference_complete_count:,} "
    f"({reference_complete_pct:.1f}%)"
)

record(
    "Airport reference available",
    "PASS",
    f"{reference_complete_count:,} records have complete endpoint "
    f"reference data ({reference_complete_pct:.1f}%)."
)


# ============================================================
# 12. Country coverage
# ============================================================

print()
print("-" * 70)
print("12. COUNTRY COVERAGE")
print("-" * 70)

departure_country_known = int(
    df["departure_airport_country_code"].notna().sum()
)

arrival_country_known = int(
    df["arrival_airport_country_code"].notna().sum()
)

departure_pct = (
    departure_country_known / len(df) * 100
    if len(df) > 0
    else 0
)

arrival_pct = (
    arrival_country_known / len(df) * 100
    if len(df) > 0
    else 0
)

print(
    f"Known departure country: "
    f"{departure_country_known:,} "
    f"({departure_pct:.1f}%)"
)

print(
    f"Known arrival country: "
    f"{arrival_country_known:,} "
    f"({arrival_pct:.1f}%)"
)

record(
    "Departure country enrichment",
    "PASS",
    f"{departure_country_known:,} records have known departure country "
    f"({departure_pct:.1f}%)."
)

record(
    "Arrival country enrichment",
    "PASS",
    f"{arrival_country_known:,} records have known arrival country "
    f"({arrival_pct:.1f}%)."
)


# ============================================================
# 13. Germany validation
# ============================================================

print()
print("-" * 70)
print("13. GERMANY VALIDATION")
print("-" * 70)

departure_germany = int(
    df["departure_is_germany"]
    .fillna(False)
    .sum()
)

arrival_germany = int(
    df["arrival_is_germany"]
    .fillna(False)
    .sum()
)

print(
    f"Departures from Germany: {departure_germany:,}"
)

print(
    f"Arrivals to Germany:      {arrival_germany:,}"
)


departure_germany_expected = (
    df["departure_airport_country_code"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("DE")
)

arrival_germany_expected = (
    df["arrival_airport_country_code"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("DE")
)

departure_germany_actual = (
    df["departure_is_germany"]
    .fillna(False)
    .astype(bool)
)

arrival_germany_actual = (
    df["arrival_is_germany"]
    .fillna(False)
    .astype(bool)
)

departure_germany_ok = (
    departure_germany_expected
    ==
    departure_germany_actual
)

arrival_germany_ok = (
    arrival_germany_expected
    ==
    arrival_germany_actual
)

if departure_germany_ok.all() and arrival_germany_ok.all():

    record(
        "Germany flags",
        "PASS",
        "Germany flags match airport country code DE."
    )

else:

    mismatches = (
        int((~departure_germany_ok).sum())
        +
        int((~arrival_germany_ok).sum())
    )

    record(
        "Germany flags",
        "FAIL",
        f"{mismatches:,} Germany flag mismatches."
    )


# ============================================================
# 14. Europe validation
#
# IMPORTANT:
# OurAirports uses "EU" as the continent code for Europe.
# ============================================================

print()
print("-" * 70)
print("14. EUROPE VALIDATION")
print("-" * 70)

departure_europe_expected = (
    df["departure_airport_continent"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("EU")
)

arrival_europe_expected = (
    df["arrival_airport_continent"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("EU")
)

departure_europe_actual = (
    df["departure_is_europe"]
    .fillna(False)
    .astype(bool)
)

arrival_europe_actual = (
    df["arrival_is_europe"]
    .fillna(False)
    .astype(bool)
)

departure_europe_ok = (
    departure_europe_expected
    ==
    departure_europe_actual
)

arrival_europe_ok = (
    arrival_europe_expected
    ==
    arrival_europe_actual
)

departure_europe_mismatches = int(
    (~departure_europe_ok).sum()
)

arrival_europe_mismatches = int(
    (~arrival_europe_ok).sum()
)

if (
    departure_europe_mismatches == 0
    and arrival_europe_mismatches == 0
):

    record(
        "Europe flags",
        "PASS",
        "Europe flags correctly match OurAirports continent code EU."
    )

else:

    record(
        "Europe flags",
        "FAIL",
        f"Departure mismatches: {departure_europe_mismatches:,}; "
        f"arrival mismatches: {arrival_europe_mismatches:,}."
    )


# ============================================================
# 15. Both endpoints in Europe
# ============================================================

print()
print("-" * 70)
print("15. BOTH ENDPOINTS IN EUROPE")
print("-" * 70)

both_europe_expected = (
    departure_europe_actual
    &
    arrival_europe_actual
)

both_europe_actual = (
    df["both_endpoints_in_europe"]
    .fillna(False)
    .astype(bool)
)

both_europe_ok = (
    both_europe_expected
    ==
    both_europe_actual
)

both_europe_mismatches = int(
    (~both_europe_ok).sum()
)

if both_europe_mismatches == 0:

    record(
        "Both endpoints in Europe",
        "PASS",
        "both_endpoints_in_europe is logically consistent."
    )

else:

    record(
        "Both endpoints in Europe",
        "FAIL",
        f"{both_europe_mismatches:,} inconsistent rows."
    )


# ============================================================
# 16. Airport reference complete flag
# ============================================================

print()
print("-" * 70)
print("16. AIRPORT REFERENCE FLAG")
print("-" * 70)

reference_expected = (
    df["departure_airport_country_code"].notna()
    &
    df["arrival_airport_country_code"].notna()
)

reference_actual = (
    df["airport_reference_complete"]
    .fillna(False)
    .astype(bool)
)

reference_ok = (
    reference_expected
    ==
    reference_actual
)

reference_mismatches = int(
    (~reference_ok).sum()
)

if reference_mismatches == 0:

    record(
        "Airport reference flag",
        "PASS",
        "airport_reference_complete is logically consistent."
    )

else:

    record(
        "Airport reference flag",
        "FAIL",
        f"{reference_mismatches:,} inconsistent rows."
    )


# ============================================================
# 17. Geographic scope values
# ============================================================

print()
print("-" * 70)
print("17. GEOGRAPHIC SCOPE")
print("-" * 70)

allowed_scopes = {
    "Germany + Europe",
    "Germany/Europe + Outside Europe",
    "Outside Europe",
    "Unknown",
}

actual_scopes = set(
    df["network_geographic_scope"]
    .dropna()
    .astype(str)
    .unique()
)

unexpected_scopes = sorted(
    actual_scopes - allowed_scopes
)

if not unexpected_scopes:

    record(
        "Geographic scope values",
        "PASS",
        "All network geographic scope values are valid."
    )

else:

    record(
        "Geographic scope values",
        "FAIL",
        "Unexpected values: " + ", ".join(unexpected_scopes)
    )


# ============================================================
# 18. Geographic scope distribution
# ============================================================

print()
print("Geographic scope distribution:")

scope_counts = (
    df["network_geographic_scope"]
    .fillna("Unknown")
    .value_counts()
)

for scope, count in scope_counts.items():

    pct = count / len(df) * 100

    print(
        f"  {scope:<35}"
        f"{count:>10,}"
        f" ({pct:5.1f}%)"
    )


# ============================================================
# 19. Geographic scope logic
# ============================================================

print()
print("-" * 70)
print("18. GEOGRAPHIC SCOPE LOGIC")
print("-" * 70)


def calculate_expected_scope(row):

    departure_country_known = pd.notna(
        row["departure_airport_country_code"]
    )

    arrival_country_known = pd.notna(
        row["arrival_airport_country_code"]
    )

    if not departure_country_known or not arrival_country_known:
        return "Unknown"

    departure_europe = bool(
        row["departure_is_europe"]
    )

    arrival_europe = bool(
        row["arrival_is_europe"]
    )

    if departure_europe and arrival_europe:
        return "Germany + Europe"

    if departure_europe or arrival_europe:
        return "Germany/Europe + Outside Europe"

    return "Outside Europe"


expected_scopes = df.apply(
    calculate_expected_scope,
    axis=1
)

actual_scopes_series = (
    df["network_geographic_scope"]
    .fillna("Unknown")
    .astype(str)
)

scope_mismatches = int(
    (expected_scopes != actual_scopes_series).sum()
)

if scope_mismatches == 0:

    record(
        "Geographic scope logic",
        "PASS",
        "Network geographic scope is logically consistent."
    )

else:

    record(
        "Geographic scope logic",
        "FAIL",
        f"{scope_mismatches:,} geographic scope mismatches."
    )


# ============================================================
# 20. Route completeness
# ============================================================

print()
print("-" * 70)
print("19. ROUTE COMPLETENESS")
print("-" * 70)

complete_route_count = int(
    df["has_complete_route"]
    .fillna(False)
    .sum()
)

complete_route_pct = (
    complete_route_count / len(df) * 100
    if len(df) > 0
    else 0
)

incomplete_route_count = (
    len(df) - complete_route_count
)

print(
    f"Complete routes:   "
    f"{complete_route_count:,} "
    f"({complete_route_pct:.1f}%)"
)

print(
    f"Incomplete routes: "
    f"{incomplete_route_count:,} "
    f"({100 - complete_route_pct:.1f}%)"
)

record(
    "Route completeness",
    "PASS",
    f"{complete_route_count:,} complete routes "
    f"({complete_route_pct:.1f}%)."
)


# ============================================================
# 21. Target airline records
# ============================================================

print()
print("-" * 70)
print("20. TARGET AIRLINE COVERAGE")
print("-" * 70)

target_airline_count = int(
    df["is_target_airline"]
    .fillna(False)
    .sum()
)

target_airline_pct = (
    target_airline_count / len(df) * 100
    if len(df) > 0
    else 0
)

print(
    f"Target airline records: "
    f"{target_airline_count:,} "
    f"({target_airline_pct:.1f}%)"
)

record(
    "Target airline records",
    "PASS",
    f"{target_airline_count:,} records belong to the "
    f"8 target airlines ({target_airline_pct:.1f}%)."
)


# ============================================================
# 22. Timestamp validation
# ============================================================

print()
print("-" * 70)
print("21. TIMESTAMP VALIDATION")
print("-" * 70)

df["first_seen"] = pd.to_datetime(
    df["first_seen"],
    errors="coerce"
)

df["last_seen"] = pd.to_datetime(
    df["last_seen"],
    errors="coerce"
)

invalid_first_seen = int(
    df["first_seen"].isna().sum()
)

invalid_last_seen = int(
    df["last_seen"].isna().sum()
)

negative_duration = int(
    (
        df["last_seen"]
        <
        df["first_seen"]
    ).sum()
)

if (
    invalid_first_seen == 0
    and invalid_last_seen == 0
    and negative_duration == 0
):

    record(
        "Timestamps",
        "PASS",
        "All timestamps are valid and no negative durations exist."
    )

else:

    record(
        "Timestamps",
        "FAIL",
        f"Invalid first_seen={invalid_first_seen:,}, "
        f"invalid last_seen={invalid_last_seen:,}, "
        f"negative durations={negative_duration:,}."
    )


# ============================================================
# 23. Data quality status
# ============================================================

print()
print("-" * 70)
print("22. DATA QUALITY STATUS")
print("-" * 70)

quality_counts = (
    df["data_quality_status"]
    .fillna("Unknown")
    .value_counts()
)

for status, count in quality_counts.items():

    pct = count / len(df) * 100

    print(
        f"  {status:<25}"
        f"{count:>10,}"
        f" ({pct:5.1f}%)"
    )

record(
    "Data quality status",
    "PASS",
    "Data quality status distribution generated."
)


# ============================================================
# 24. Monthly coverage
# ============================================================

print()
print("-" * 70)
print("23. MONTHLY COVERAGE")
print("-" * 70)

monthly_counts = (
    df.assign(
        month=df["flight_date"]
        .dt.to_period("M")
        .astype(str)
    )
    .groupby("month")
    .size()
)

for month, count in monthly_counts.items():

    print(
        f"  {month}: {count:,}"
    )

record(
    "Monthly record coverage",
    "PASS",
    f"{len(monthly_counts)} months contain records."
)


# ============================================================
# 25. Top departure countries
# ============================================================

print()
print("-" * 70)
print("24. TOP DEPARTURE COUNTRIES")
print("-" * 70)

top_departure_countries = (
    df["departure_airport_country_code"]
    .dropna()
    .astype(str)
    .value_counts()
    .head(15)
)

for country, count in top_departure_countries.items():

    print(
        f"  {country}: {count:,}"
    )


# ============================================================
# 26. Top arrival countries
# ============================================================

print()
print("-" * 70)
print("25. TOP ARRIVAL COUNTRIES")
print("-" * 70)

top_arrival_countries = (
    df["arrival_airport_country_code"]
    .dropna()
    .astype(str)
    .value_counts()
    .head(15)
)

for country, count in top_arrival_countries.items():

    print(
        f"  {country}: {count:,}"
    )


# ============================================================
# 27. BigQuery readiness
# ============================================================

print()
print("-" * 70)
print("26. BIGQUERY READINESS")
print("-" * 70)

critical_tests = [
    "Rows exist",
    "Expected schema",
    "Valid flight dates",
    "All 12 months present",
    "Records inside 12-month window",
    "Duplicate flight IDs",
    "All target airports present",
    "All target airlines present",
    "Target airline mapping",
    "Airline categories",
    "Germany flags",
    "Europe flags",
    "Both endpoints in Europe",
    "Airport reference flag",
    "Geographic scope values",
    "Geographic scope logic",
    "Timestamps",
]

critical_results = {
    item["test"]: item["status"]
    for item in results
}

failed_critical = [
    test
    for test in critical_tests
    if critical_results.get(test) != "PASS"
]

if not failed_critical:

    record(
        "BigQuery readiness",
        "PASS",
        "All critical validation checks passed."
    )

else:

    record(
        "BigQuery readiness",
        "FAIL",
        "Critical failures: " + ", ".join(failed_critical)
    )


# ============================================================
# Save report
# ============================================================

print()
print("-" * 70)
print("27. SAVING VALIDATION REPORT")
print("-" * 70)

report_df = pd.DataFrame(results)

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

report_df.to_csv(
    REPORT_FILE,
    index=False
)

print()
print("Validation report saved to:")
print(REPORT_FILE)


# ============================================================
# Final summary
# ============================================================

passed = sum(
    1
    for item in results
    if item["status"] == "PASS"
)

failed = sum(
    1
    for item in results
    if item["status"] == "FAIL"
)

print()
print("=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

print(
    f"PASS: {passed}"
)

print(
    f"FAIL: {failed}"
)

print()
print(
    f"Records: {len(df):,}"
)

print(
    f"Date range: "
    f"{min_date.date()} → {max_date.date()}"
)

print(
    f"Complete airport reference: "
    f"{reference_complete_count:,} "
    f"({reference_complete_pct:.1f}%)"
)

print(
    f"Both endpoints in Europe: "
    f"{int(df['both_endpoints_in_europe'].fillna(False).sum()):,}"
)

print(
    f"Target airline records: "
    f"{target_airline_count:,} "
    f"({target_airline_pct:.1f}%)"
)

print()

if failed == 0:

    print(
        "RESULT: PASS — enriched dataset is ready for the next stage."
    )

else:

    print(
        "RESULT: REVIEW REQUIRED — "
        "please check the failed validation tests before BigQuery."
    )

print("=" * 70)