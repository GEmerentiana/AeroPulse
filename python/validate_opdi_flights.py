from pathlib import Path
import pandas as pd


# ============================================================
# AeroPulse — Validate Processed OPDI Flight Data
# ============================================================
#
# Purpose:
# Validate the processed OPDI flight dataset before loading
# it into BigQuery.
#
# IMPORTANT:
# This validator matches the actual 38-column schema produced
# by transform_opdi_flights.py.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opdi"
    / "aeropulse_flights.parquet"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opdi"
)

QUALITY_FILE = (
    OUTPUT_DIR
    / "validation_report.csv"
)


# ------------------------------------------------------------
# 2. CONFIGURATION
# ------------------------------------------------------------

TARGET_AIRPORTS = {
    "EDDF": "FRA",
    "EDDM": "MUC",
    "EDDB": "BER",
    "EDDL": "DUS",
    "EDDH": "HAM",
}


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


EXPECTED_COLUMNS = [
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


# ------------------------------------------------------------
# HELPER
# ------------------------------------------------------------

def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_pass(message):
    print(f"[PASS] {message}")


def print_fail(message):
    print(f"[FAIL] {message}")


def print_info(message):
    print(f"[INFO] {message}")


# ------------------------------------------------------------
# 3. INPUT FILE
# ------------------------------------------------------------

print_section("1. INPUT FILE")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Processed OPDI file not found:\n{INPUT_FILE}"
    )

print(f"Input file:")
print(INPUT_FILE)

df = pd.read_parquet(INPUT_FILE)

print(f"Rows:    {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ------------------------------------------------------------
# 4. SCHEMA VALIDATION
# ------------------------------------------------------------

print_section("2. SCHEMA VALIDATION")

actual_columns = list(df.columns)

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

unexpected_columns = [
    column
    for column in actual_columns
    if column not in EXPECTED_COLUMNS
]


if not missing_columns:
    print_pass(
        "All expected columns are present."
    )
else:
    print_fail("Missing columns:")
    for column in missing_columns:
        print(f"  - {column}")


if unexpected_columns:
    print_info(
        "Additional columns found:"
    )

    for column in unexpected_columns:
        print(f"  - {column}")

else:
    print_pass(
        "No unexpected columns found."
    )


# ------------------------------------------------------------
# 5. DATA TYPES
# ------------------------------------------------------------

print_section("3. DATA TYPES")

print(df.dtypes.to_string())


# ------------------------------------------------------------
# 6. DATE COVERAGE
# ------------------------------------------------------------

print_section("4. DATE COVERAGE")

df["flight_date"] = pd.to_datetime(
    df["flight_date"],
    errors="coerce"
)

invalid_flight_dates = df[
    df["flight_date"].isna()
]

print(
    f"Invalid flight dates: "
    f"{len(invalid_flight_dates):,}"
)

if len(invalid_flight_dates) == 0:
    print_pass(
        "All flight_date values are valid."
    )
else:
    print_fail(
        "Some flight_date values could not be parsed."
    )


min_date = df["flight_date"].min()
max_date = df["flight_date"].max()

print(
    f"Minimum flight date: {min_date}"
)

print(
    f"Maximum flight date: {max_date}"
)


# ------------------------------------------------------------
# 7. MONTHLY COVERAGE
# ------------------------------------------------------------

print_section("5. RECORDS BY MONTH")

df["month"] = (
    df["flight_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_counts = (
    df
    .groupby("month")
    .size()
    .reset_index(name="records")
)

print(
    monthly_counts.to_string(index=False)
)


EXPECTED_MONTHS = [
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
    "2026-06",
    "2026-07",
]

actual_months = monthly_counts["month"].tolist()

missing_months = [
    month
    for month in EXPECTED_MONTHS
    if month not in actual_months
]

if not missing_months:
    print_pass(
        "All 12 expected months are present."
    )
else:
    print_fail(
        f"Missing months: {missing_months}"
    )


# ------------------------------------------------------------
# 8. 12-MONTH WINDOW
# ------------------------------------------------------------

print_section("6. 12-MONTH WINDOW")

EXPECTED_START = pd.Timestamp(
    "2025-08-01"
)

EXPECTED_END = pd.Timestamp(
    "2026-07-31"
)

outside_window = df[
    (df["flight_date"] < EXPECTED_START)
    |
    (df["flight_date"] > EXPECTED_END)
]

print(
    f"Expected start: {EXPECTED_START.date()}"
)

print(
    f"Expected end:   {EXPECTED_END.date()}"
)

print(
    f"Outside window: {len(outside_window):,}"
)

if len(outside_window) == 0:
    print_pass(
        "All records are inside the required "
        "12-month window."
    )
else:
    print_fail(
        "Some records fall outside the required "
        "12-month window."
    )


# ------------------------------------------------------------
# 9. NULL CHECK
# ------------------------------------------------------------

print_section("7. NULL / MISSING VALUE CHECK")

null_counts = df.isna().sum()

null_table = (
    null_counts[
        null_counts > 0
    ]
    .sort_values(
        ascending=False
    )
    .to_frame(
        "null_count"
    )
)

if len(null_table) == 0:

    print_pass(
        "No null values found."
    )

else:

    null_table["null_pct"] = (
        null_table["null_count"]
        / len(df)
        * 100
    )

    print(
        null_table.to_string()
    )

    print()

    print_info(
        "Missing values can be expected in OPDI "
        "airport/operator/aircraft enrichment fields."
    )


# ------------------------------------------------------------
# 10. DUPLICATE FLIGHT IDs
# ------------------------------------------------------------

print_section("8. DUPLICATE FLIGHT IDs")

duplicate_mask = (
    df["flight_id"]
    .duplicated(
        keep=False
    )
)

duplicate_count = (
    duplicate_mask.sum()
)

print(
    f"Duplicate flight IDs: "
    f"{duplicate_count:,}"
)

if duplicate_count == 0:
    print_pass(
        "No duplicate flight IDs found."
    )
else:
    print_fail(
        "Duplicate flight IDs exist."
    )

    print(
        df.loc[
            duplicate_mask,
            [
                "flight_id",
                "flight_date",
                "departure_airport_icao",
                "arrival_airport_icao",
            ],
        ]
        .head(20)
        .to_string(index=False)
    )


# ------------------------------------------------------------
# 11. TARGET AIRPORT VALIDATION
# ------------------------------------------------------------

print_section("9. TARGET AIRPORT VALIDATION")

airport_results = []

for icao, iata in TARGET_AIRPORTS.items():

    departures = (
        df["departure_airport_icao"]
        .eq(icao)
        .sum()
    )

    arrivals = (
        df["arrival_airport_icao"]
        .eq(icao)
        .sum()
    )

    total_activity = (
        departures + arrivals
    )

    airport_results.append(
        {
            "airport_icao": icao,
            "airport_iata": iata,
            "departures": departures,
            "arrivals": arrivals,
            "total_activity": total_activity,
        }
    )


airport_summary = pd.DataFrame(
    airport_results
)

print(
    airport_summary.to_string(
        index=False
    )
)


missing_airports = airport_summary[
    airport_summary["total_activity"] == 0
]


if len(missing_airports) == 0:

    print_pass(
        "All five target airports have activity."
    )

else:

    print_fail(
        "At least one target airport has no activity."
    )


# ------------------------------------------------------------
# 12. AIRPORT ACTIVITY BY MONTH
# ------------------------------------------------------------

print_section("10. AIRPORT ACTIVITY BY MONTH")

airport_monthly = []

for icao, iata in TARGET_AIRPORTS.items():

    subset = df[
        (
            df["departure_airport_icao"]
            == icao
        )
        |
        (
            df["arrival_airport_icao"]
            == icao
        )
    ]

    monthly = (
        subset
        .groupby("month")
        .size()
        .reset_index(
            name="records"
        )
    )

    monthly["airport_icao"] = icao
    monthly["airport_iata"] = iata

    airport_monthly.append(
        monthly
    )


airport_monthly_df = pd.concat(
    airport_monthly,
    ignore_index=True
)

print(
    airport_monthly_df[
        [
            "month",
            "airport_iata",
            "records",
        ]
    ]
    .sort_values(
        [
            "month",
            "airport_iata",
        ]
    )
    .to_string(index=False)
)


# ------------------------------------------------------------
# 13. TARGET AIRLINE VALIDATION
# ------------------------------------------------------------

print_section("11. TARGET AIRLINE VALIDATION")

airline_results = []

for operator, airline in TARGET_AIRLINES.items():

    count = (
        df["icao_operator"]
        .eq(operator)
        .sum()
    )

    airline_results.append(
        {
            "operator_icao": operator,
            "airline_name": airline,
            "records": count,
        }
    )


airline_summary = pd.DataFrame(
    airline_results
)

print(
    airline_summary.to_string(
        index=False
    )
)


missing_airlines = airline_summary[
    airline_summary["records"] == 0
]


if len(missing_airlines) == 0:

    print_pass(
        "All eight target airline operator codes "
        "are present."
    )

else:

    print_fail(
        "At least one target airline operator code "
        "is missing."
    )


# ------------------------------------------------------------
# 14. TARGET AIRLINE FLAG
# ------------------------------------------------------------

print_section("12. TARGET AIRLINE FLAG")

target_airline_count = (
    df["is_target_airline"]
    .fillna(False)
    .sum()
)

target_airline_pct = (
    target_airline_count
    / len(df)
    * 100
)

print(
    f"Target-airline records: "
    f"{target_airline_count:,}"
)

print(
    f"Target-airline percentage: "
    f"{target_airline_pct:.1f}%"
)


# ------------------------------------------------------------
# 15. AIRLINE NAME CONSISTENCY
# ------------------------------------------------------------

print_section("13. AIRLINE MAPPING CONSISTENCY")

for operator, expected_name in TARGET_AIRLINES.items():

    subset = df[
        df["icao_operator"] == operator
    ]

    actual_names = (
        subset["airline_name"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        f"{operator}: "
        f"{expected_name}"
    )

    print(
        f"  Records: {len(subset):,}"
    )

    print(
        f"  Names found: {actual_names}"
    )


# ------------------------------------------------------------
# 16. AIRLINE CATEGORY
# ------------------------------------------------------------

print_section("14. AIRLINE CATEGORY")

category_counts = (
    df["airline_category"]
    .value_counts(
        dropna=False
    )
)

print(
    category_counts.to_string()
)


# ------------------------------------------------------------
# 17. OPERATOR COMPLETENESS
# ------------------------------------------------------------

print_section("15. OPERATOR COMPLETENESS")

known_operator_count = (
    df["has_known_operator"]
    .fillna(False)
    .sum()
)

known_operator_pct = (
    known_operator_count
    / len(df)
    * 100
)

unknown_operator_count = (
    len(df)
    - known_operator_count
)

print(
    f"Known operators: "
    f"{known_operator_count:,} "
    f"({known_operator_pct:.1f}%)"
)

print(
    f"Unknown operators: "
    f"{unknown_operator_count:,} "
    f"({100 - known_operator_pct:.1f}%)"
)


# ------------------------------------------------------------
# 18. CALLSIGN COMPLETENESS
# ------------------------------------------------------------

print_section("16. CALLSIGN COMPLETENESS")

known_callsign_count = (
    df["has_known_callsign"]
    .fillna(False)
    .sum()
)

known_callsign_pct = (
    known_callsign_count
    / len(df)
    * 100
)

print(
    f"Known callsigns: "
    f"{known_callsign_count:,} "
    f"({known_callsign_pct:.1f}%)"
)


# ------------------------------------------------------------
# 19. ROUTE COMPLETENESS
# ------------------------------------------------------------

print_section("17. ROUTE COMPLETENESS")

known_departure_count = (
    df["has_known_departure"]
    .fillna(False)
    .sum()
)

known_arrival_count = (
    df["has_known_arrival"]
    .fillna(False)
    .sum()
)

complete_route_count = (
    df["has_complete_route"]
    .fillna(False)
    .sum()
)

complete_route_pct = (
    complete_route_count
    / len(df)
    * 100
)

print(
    f"Known departures: "
    f"{known_departure_count:,}"
)

print(
    f"Known arrivals: "
    f"{known_arrival_count:,}"
)

print(
    f"Complete routes: "
    f"{complete_route_count:,} "
    f"({complete_route_pct:.1f}%)"
)

print(
    f"Incomplete routes: "
    f"{len(df) - complete_route_count:,}"
)


# ------------------------------------------------------------
# 20. TARGET AIRPORT FLAGS
# ------------------------------------------------------------

print_section("18. TARGET AIRPORT FLAGS")

departure_flag_count = (
    df["is_target_airport_departure"]
    .fillna(False)
    .sum()
)

arrival_flag_count = (
    df["is_target_airport_arrival"]
    .fillna(False)
    .sum()
)

print(
    f"Target-airport departures: "
    f"{departure_flag_count:,}"
)

print(
    f"Target-airport arrivals: "
    f"{arrival_flag_count:,}"
)

print(
    f"Total records: "
    f"{len(df):,}"
)


# ------------------------------------------------------------
# 21. TARGET AIRPORT ROLE
# ------------------------------------------------------------

print_section("19. TARGET AIRPORT ROLE")

role_counts = (
    df["target_airport_role"]
    .value_counts(
        dropna=False
    )
)

print(
    role_counts.to_string()
)


# ------------------------------------------------------------
# 22. ROUTE DIRECTION
# ------------------------------------------------------------

print_section("20. ROUTE DIRECTION")

direction_counts = (
    df["route_direction"]
    .value_counts(
        dropna=False
    )
)

print(
    direction_counts.to_string()
)


# ------------------------------------------------------------
# 23. COUNTRY COVERAGE
# ------------------------------------------------------------

print_section("21. COUNTRY COVERAGE")

departure_country_counts = (
    df["departure_country"]
    .value_counts(
        dropna=False
    )
    .head(20)
)

arrival_country_counts = (
    df["arrival_country"]
    .value_counts(
        dropna=False
    )
    .head(20)
)

print("Top departure countries:")
print(
    departure_country_counts.to_string()
)

print()

print("Top arrival countries:")
print(
    arrival_country_counts.to_string()
)


# ------------------------------------------------------------
# 24. GERMANY CHECK
# ------------------------------------------------------------

print_section("22. GERMANY ROUTE CHECK")

germany_departures = (
    df["departure_country"]
    .eq("Germany")
    .sum()
)

germany_arrivals = (
    df["arrival_country"]
    .eq("Germany")
    .sum()
)

print(
    f"Records departing from Germany: "
    f"{germany_departures:,}"
)

print(
    f"Records arriving in Germany: "
    f"{germany_arrivals:,}"
)

print_info(
    "Europe-wide validation will be finalized after "
    "the airport reference/enrichment step."
)


# ------------------------------------------------------------
# 25. TIMESTAMP VALIDATION
# ------------------------------------------------------------

print_section("23. TIMESTAMP VALIDATION")

df["first_seen"] = pd.to_datetime(
    df["first_seen"],
    errors="coerce"
)

df["last_seen"] = pd.to_datetime(
    df["last_seen"],
    errors="coerce"
)

invalid_timestamp_mask = (
    df["first_seen"].isna()
    |
    df["last_seen"].isna()
    |
    (
        df["last_seen"]
        < df["first_seen"]
    )
)

invalid_timestamp_count = (
    invalid_timestamp_mask.sum()
)

print(
    f"Invalid timestamp records: "
    f"{invalid_timestamp_count:,}"
)

if invalid_timestamp_count == 0:

    print_pass(
        "All first_seen/last_seen timestamps are valid."
    )

else:

    print_fail(
        "Some records have invalid timestamps."
    )


# ------------------------------------------------------------
# 26. OBSERVATION DURATION
# ------------------------------------------------------------

print_section("24. OBSERVATION DURATION")

duration = pd.to_numeric(
    df["observation_duration_minutes"],
    errors="coerce"
)

print(
    duration.describe().to_string()
)

negative_duration_count = (
    duration < 0
).sum()

print(
    f"Negative durations: "
    f"{negative_duration_count:,}"
)

if negative_duration_count == 0:

    print_pass(
        "No negative observation durations found."
    )

else:

    print_fail(
        "Negative observation durations exist."
    )


# ------------------------------------------------------------
# 27. ROUTE COMPLETENESS BY MONTH
# ------------------------------------------------------------

print_section("25. ROUTE COMPLETENESS BY MONTH")

route_monthly = (
    df
    .groupby("month")
    .agg(
        total_records=(
            "flight_id",
            "count"
        ),
        complete_routes=(
            "has_complete_route",
            "sum"
        ),
    )
    .reset_index()
)

route_monthly["complete_route_pct"] = (
    route_monthly["complete_routes"]
    / route_monthly["total_records"]
    * 100
)

print(
    route_monthly.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 28. TARGET AIRLINE BY MONTH
# ------------------------------------------------------------

print_section("26. TARGET AIRLINES BY MONTH")

target_airline_monthly = (
    df[
        df["is_target_airline"]
        .fillna(False)
    ]
    .groupby(
        [
            "month",
            "airline_name",
        ]
    )
    .size()
    .reset_index(
        name="records"
    )
)

print(
    target_airline_monthly
    .sort_values(
        [
            "month",
            "records",
        ],
        ascending=[
            True,
            False,
        ],
    )
    .to_string(index=False)
)


# ------------------------------------------------------------
# 29. ROUTE SAMPLE
# ------------------------------------------------------------

print_section("27. TOP ROUTES")

route_counts = (
    df[
        df["route_icao"]
        .notna()
        &
        df["route_icao"].ne("")
    ]
    ["route_icao"]
    .value_counts()
    .head(20)
)

print(
    route_counts.to_string()
)


# ------------------------------------------------------------
# 30. SAMPLE RECORDS
# ------------------------------------------------------------

print_section("28. SAMPLE RECORDS")

sample_columns = [
    "flight_id",
    "callsign",
    "flight_date",
    "departure_airport_icao",
    "arrival_airport_icao",
    "departure_airport_iata",
    "arrival_airport_iata",
    "departure_country",
    "arrival_country",
    "icao_operator",
    "airline_name",
    "airline_category",
    "first_seen",
    "last_seen",
    "observation_duration_minutes",
    "route_icao",
    "route_iata",
    "target_airport_role",
    "is_target_airline",
    "data_quality_status",
]

available_sample_columns = [
    column
    for column in sample_columns
    if column in df.columns
]

print(
    df[
        available_sample_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 31. DATA QUALITY STATUS
# ------------------------------------------------------------

print_section("29. DATA QUALITY STATUS")

quality_counts = (
    df["data_quality_status"]
    .value_counts(
        dropna=False
    )
)

print(
    quality_counts.to_string()
)


# ------------------------------------------------------------
# 32. BIGQUERY READINESS CHECKS
# ------------------------------------------------------------

print_section("30. BIGQUERY READINESS")

checks = {
    "Rows exist": (
        len(df) > 0
    ),

    "Required columns exist": (
        len(missing_columns) == 0
    ),

    "All 12 months present": (
        len(missing_months) == 0
    ),

    "Dates inside 12-month window": (
        len(outside_window) == 0
    ),

    "No duplicate flight IDs": (
        duplicate_count == 0
    ),

    "All target airports present": (
        len(missing_airports) == 0
    ),

    "All target airlines present": (
        len(missing_airlines) == 0
    ),

    "No invalid flight dates": (
        len(invalid_flight_dates) == 0
    ),

    "No invalid timestamps": (
        invalid_timestamp_count == 0
    ),

    "No negative observation durations": (
        negative_duration_count == 0
    ),
}


for check_name, result in checks.items():

    if result:
        print_pass(check_name)
    else:
        print_fail(check_name)


all_passed = all(
    checks.values()
)


# ------------------------------------------------------------
# 33. SAVE VALIDATION REPORT
# ------------------------------------------------------------

print_section("31. SAVE VALIDATION REPORT")

report_rows = [
    {
        "check": "row_count",
        "value": len(df),
        "status": (
            "PASS"
            if len(df) > 0
            else "FAIL"
        ),
    },

    {
        "check": "column_count",
        "value": len(df.columns),
        "status": "PASS",
    },

    {
        "check": "minimum_date",
        "value": str(
            min_date.date()
        ),
        "status": "PASS",
    },

    {
        "check": "maximum_date",
        "value": str(
            max_date.date()
        ),
        "status": "PASS",
    },

    {
        "check": "missing_months",
        "value": len(
            missing_months
        ),
        "status": (
            "PASS"
            if not missing_months
            else "FAIL"
        ),
    },

    {
        "check": "outside_12_month_window",
        "value": len(
            outside_window
        ),
        "status": (
            "PASS"
            if len(outside_window) == 0
            else "FAIL"
        ),
    },

    {
        "check": "duplicate_flight_ids",
        "value": duplicate_count,
        "status": (
            "PASS"
            if duplicate_count == 0
            else "FAIL"
        ),
    },

    {
        "check": "complete_routes",
        "value": complete_route_count,
        "status": "INFO",
    },

    {
        "check": "complete_route_percentage",
        "value": round(
            complete_route_pct,
            2
        ),
        "status": "INFO",
    },

    {
        "check": "known_operators",
        "value": known_operator_count,
        "status": "INFO",
    },

    {
        "check": "known_operator_percentage",
        "value": round(
            known_operator_pct,
            2
        ),
        "status": "INFO",
    },

    {
        "check": "known_callsigns",
        "value": known_callsign_count,
        "status": "INFO",
    },

    {
        "check": "known_callsign_percentage",
        "value": round(
            known_callsign_pct,
            2
        ),
        "status": "INFO",
    },

    {
        "check": "target_airline_records",
        "value": target_airline_count,
        "status": "INFO",
    },

    {
        "check": "target_airline_percentage",
        "value": round(
            target_airline_pct,
            2
        ),
        "status": "INFO",
    },

    {
        "check": "invalid_flight_dates",
        "value": len(
            invalid_flight_dates
        ),
        "status": (
            "PASS"
            if len(invalid_flight_dates) == 0
            else "FAIL"
        ),
    },

    {
        "check": "invalid_timestamps",
        "value": invalid_timestamp_count,
        "status": (
            "PASS"
            if invalid_timestamp_count == 0
            else "FAIL"
        ),
    },

    {
        "check": "negative_observation_durations",
        "value": negative_duration_count,
        "status": (
            "PASS"
            if negative_duration_count == 0
            else "FAIL"
        ),
    },
]


validation_report = pd.DataFrame(
    report_rows
)

validation_report.to_csv(
    QUALITY_FILE,
    index=False
)

print(
    f"Saved validation report:"
)

print(
    QUALITY_FILE
)


# ------------------------------------------------------------
# 34. FINAL RESULT
# ------------------------------------------------------------

print_section("32. FINAL RESULT")

if all_passed:

    print(
        "[PASS] Processed OPDI flight data "
        "passed the BigQuery readiness checks."
    )

    print()

    print(
        "The dataset can proceed to the "
        "next pipeline stage."
    )

else:

    print(
        "[WARNING] One or more BigQuery "
        "readiness checks failed."
    )

    print()

    print(
        "Review the failed checks above "
        "before loading into BigQuery."
    )


print()
print("Validation complete.")