"""
AeroPulse — OPDI Historical Flight Transformation

Purpose
-------
Transform the monthly OPDI Flight List Parquet files
into a clean AeroPulse historical flight dataset.

Historical window
-----------------
August 2025 through July 2026

Source
------
Open Performance Data Initiative (OPDI)

Important terminology
---------------------
OPDI flight records are observed/reconstructed flight activity
derived from ADS-B data.

Therefore, this dataset should NOT be described as:
- scheduled commercial flights
- passenger demand
- market share
- airline revenue
- profitability

This script:
- reads all monthly OPDI files
- handles minor schema differences between monthly files
- standardizes fields
- filters to the AeroPulse airport network
- maps validated airline operator codes
- creates route attributes
- creates data-quality flags
- removes exact duplicate flight IDs
- writes a processed Parquet dataset
- writes a quality report

Raw OPDI files are never modified.
"""

from __future__ import annotations

from pathlib import Path
import time

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "opdi"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opdi"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "aeropulse_flights.parquet"
)

QUALITY_REPORT_FILE = (
    PROCESSED_DIR
    / "opdi_quality_report.csv"
)


# ============================================================
# HISTORICAL WINDOW
# ============================================================

START_DATE = pd.Timestamp("2025-08-01")
END_DATE = pd.Timestamp("2026-07-31")


# ============================================================
# TARGET AIRPORTS
# ============================================================

TARGET_AIRPORTS = {

    "EDDF": {
        "iata": "FRA",
        "name": "Frankfurt Airport",
        "country": "Germany",
    },

    "EDDM": {
        "iata": "MUC",
        "name": "Munich Airport",
        "country": "Germany",
    },

    "EDDB": {
        "iata": "BER",
        "name": "Berlin Brandenburg Airport",
        "country": "Germany",
    },

    "EDDL": {
        "iata": "DUS",
        "name": "Düsseldorf Airport",
        "country": "Germany",
    },

    "EDDH": {
        "iata": "HAM",
        "name": "Hamburg Airport",
        "country": "Germany",
    },
}


TARGET_AIRPORT_ICAO = set(
    TARGET_AIRPORTS.keys()
)


# ============================================================
# TARGET AIRLINES
# ============================================================

TARGET_AIRLINES = {

    "DLH": {
        "airline_name": "Lufthansa",
        "airline_category": "Legacy",
    },

    "AFR": {
        "airline_name": "Air France",
        "airline_category": "Legacy",
    },

    "KLM": {
        "airline_name": "KLM",
        "airline_category": "Legacy",
    },

    "BAW": {
        "airline_name": "British Airways",
        "airline_category": "Legacy",
    },

    "RYR": {
        "airline_name": "Ryanair",
        "airline_category": "Low-cost",
    },

    "EZY": {
        "airline_name": "easyJet",
        "airline_category": "Low-cost",
    },

    "WZZ": {
        "airline_name": "Wizz Air",
        "airline_category": "Low-cost",
    },

    "EWG": {
        "airline_name": "Eurowings",
        "airline_category": "Low-cost",
    },
}


TARGET_AIRLINE_CODES = set(
    TARGET_AIRLINES.keys()
)


# ============================================================
# REQUIRED SOURCE COLUMNS
# ============================================================

REQUIRED_SOURCE_COLUMNS = [
    "id",
    "icao24",
    "flt_id",
    "dof",
    "adep",
    "ades",
    "adep_p",
    "ades_p",
    "registration",
    "model",
    "typecode",
    "icao_aircraft_class",
    "icao_operator",
    "first_seen",
    "last_seen",
    "version",
]


# ============================================================
# OUTPUT COLUMNS
# ============================================================

OUTPUT_COLUMNS = [

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(title: str) -> None:

    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


def clean_string(series: pd.Series) -> pd.Series:

    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )


def get_airport_iata(icao_code: str) -> str:

    information = TARGET_AIRPORTS.get(
        icao_code
    )

    if information is None:
        return ""

    return information["iata"]


def get_airport_name(icao_code: str) -> str:

    information = TARGET_AIRPORTS.get(
        icao_code
    )

    if information is None:
        return ""

    return information["name"]


def get_airport_country(icao_code: str) -> str:

    information = TARGET_AIRPORTS.get(
        icao_code
    )

    if information is None:
        return ""

    return information["country"]


def get_airline_name(operator_code: str) -> str:

    information = TARGET_AIRLINES.get(
        operator_code
    )

    if information is None:
        return ""

    return information["airline_name"]


def get_airline_category(operator_code: str) -> str:

    information = TARGET_AIRLINES.get(
        operator_code
    )

    if information is None:
        return ""

    return information["airline_category"]


# ============================================================
# TRANSFORM ONE FILE
# ============================================================

def transform_file(
    file: Path,
) -> tuple[pd.DataFrame, dict]:

    print()
    print(f"Reading: {file.name}")

    # --------------------------------------------------------
    # Read available columns
    #
    # Some OPDI monthly files have small schema differences.
    # Therefore we first inspect the actual columns instead
    # of assuming every file contains exactly the same fields.
    # --------------------------------------------------------

    available_columns = pd.read_parquet(
        file,
        engine="pyarrow",
    ).columns.tolist()

    missing_required = [
        column
        for column in REQUIRED_SOURCE_COLUMNS
        if column not in available_columns
    ]

    if missing_required:

        raise ValueError(
            f"Missing required columns: "
            f"{missing_required}"
        )

    # --------------------------------------------------------
    # Read only the columns actually required.
    #
    # unix_time is intentionally NOT required because it is
    # absent from some monthly OPDI files and is not needed
    # for the AeroPulse analysis.
    # --------------------------------------------------------

    df = pd.read_parquet(
        file,
        columns=REQUIRED_SOURCE_COLUMNS,
        engine="pyarrow",
    )

    original_rows = len(df)

    # --------------------------------------------------------
    # Standardize flight date
    # --------------------------------------------------------

    df["flight_date"] = pd.to_datetime(
        df["dof"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # Standardize airport fields
    # --------------------------------------------------------

    df["departure_airport_icao"] = clean_string(
        df["adep"]
    )

    df["arrival_airport_icao"] = clean_string(
        df["ades"]
    )

    df["departure_airport_iata"] = (
        df["departure_airport_icao"]
        .map(get_airport_iata)
    )

    df["arrival_airport_iata"] = (
        df["arrival_airport_icao"]
        .map(get_airport_iata)
    )

    df["departure_airport_name"] = (
        df["departure_airport_icao"]
        .map(get_airport_name)
    )

    df["arrival_airport_name"] = (
        df["arrival_airport_icao"]
        .map(get_airport_name)
    )

    df["departure_country"] = (
        df["departure_airport_icao"]
        .map(get_airport_country)
    )

    df["arrival_country"] = (
        df["arrival_airport_icao"]
        .map(get_airport_country)
    )

    # --------------------------------------------------------
    # Operator
    # --------------------------------------------------------

    df["icao_operator"] = clean_string(
        df["icao_operator"]
    )

    df["airline_name"] = (
        df["icao_operator"]
        .map(get_airline_name)
    )

    df["airline_category"] = (
        df["icao_operator"]
        .map(get_airline_category)
    )

    df["airline_identification_status"] = (
        "Unknown"
    )

    df.loc[
        df["icao_operator"].isin(
            TARGET_AIRLINE_CODES
        ),
        "airline_identification_status",
    ] = "Target airline"

    df.loc[
        (
            df["icao_operator"] != ""
        )
        & ~df["icao_operator"].isin(
            TARGET_AIRLINE_CODES
        ),
        "airline_identification_status",
    ] = "Other operator"

    # --------------------------------------------------------
    # Callsign
    # --------------------------------------------------------

    df["callsign"] = (
        df["flt_id"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Aircraft fields
    # --------------------------------------------------------

    df["aircraft_model"] = (
        df["model"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["aircraft_typecode"] = (
        df["typecode"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["aircraft_class"] = (
        df["icao_aircraft_class"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["registration"] = (
        df["registration"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Observation timestamps
    # --------------------------------------------------------

    df["first_seen"] = pd.to_datetime(
        df["first_seen"],
        errors="coerce",
    )

    df["last_seen"] = pd.to_datetime(
        df["last_seen"],
        errors="coerce",
    )

    df["observation_duration_minutes"] = (
        (
            df["last_seen"]
            - df["first_seen"]
        )
        .dt.total_seconds()
        / 60
    )

    # --------------------------------------------------------
    # Known endpoint flags
    # --------------------------------------------------------

    has_departure = (
        df["departure_airport_icao"] != ""
    )

    has_arrival = (
        df["arrival_airport_icao"] != ""
    )

    df["has_known_departure"] = (
        has_departure
    )

    df["has_known_arrival"] = (
        has_arrival
    )

    df["has_complete_route"] = (
        has_departure
        & has_arrival
    )

    # --------------------------------------------------------
    # Route ICAO
    # --------------------------------------------------------

    df["route_icao"] = ""

    complete_route = (
        has_departure
        & has_arrival
    )

    df.loc[
        complete_route,
        "route_icao",
    ] = (
        df.loc[
            complete_route,
            "departure_airport_icao",
        ]
        + "-"
        + df.loc[
            complete_route,
            "arrival_airport_icao",
        ]
    )

    # --------------------------------------------------------
    # Route IATA
    #
    # IATA codes are populated only for the five target
    # airports using our validated target-airport mapping.
    # Other European airports remain blank at this stage.
    # --------------------------------------------------------

    df["route_iata"] = ""

    complete_iata_route = (
        (
            df["departure_airport_iata"]
            != ""
        )
        &
        (
            df["arrival_airport_iata"]
            != ""
        )
    )

    df.loc[
        complete_iata_route,
        "route_iata",
    ] = (
        df.loc[
            complete_iata_route,
            "departure_airport_iata",
        ]
        + "-"
        + df.loc[
            complete_iata_route,
            "arrival_airport_iata",
        ]
    )

    # --------------------------------------------------------
    # Route direction
    # --------------------------------------------------------

    df["route_direction"] = "Unknown"

    target_departure = (
        df["departure_airport_icao"].isin(
            TARGET_AIRPORT_ICAO
        )
    )

    target_arrival = (
        df["arrival_airport_icao"].isin(
            TARGET_AIRPORT_ICAO
        )
    )

    df.loc[
        target_departure
        & ~target_arrival,
        "route_direction",
    ] = "Outbound"

    df.loc[
        ~target_departure
        & target_arrival,
        "route_direction",
    ] = "Inbound"

    df.loc[
        target_departure
        & target_arrival,
        "route_direction",
    ] = "Between target airports"

    # --------------------------------------------------------
    # Target airport flags
    # --------------------------------------------------------

    df["is_target_airport_departure"] = (
        target_departure
    )

    df["is_target_airport_arrival"] = (
        target_arrival
    )

    df["target_airport_role"] = "None"

    df.loc[
        target_departure
        & ~target_arrival,
        "target_airport_role",
    ] = "Departure"

    df.loc[
        ~target_departure
        & target_arrival,
        "target_airport_role",
    ] = "Arrival"

    df.loc[
        target_departure
        & target_arrival,
        "target_airport_role",
    ] = "Between target airports"

    # --------------------------------------------------------
    # Operator quality
    # --------------------------------------------------------

    df["has_known_operator"] = (
        df["icao_operator"] != ""
    )

    # --------------------------------------------------------
    # Callsign quality
    # --------------------------------------------------------

    df["has_known_callsign"] = (
        df["callsign"] != ""
    )

    # --------------------------------------------------------
    # Target airline flag
    # --------------------------------------------------------

    df["is_target_airline"] = (
        df["icao_operator"].isin(
            TARGET_AIRLINE_CODES
        )
    )

    # --------------------------------------------------------
    # Data quality status
    # --------------------------------------------------------

    df["data_quality_status"] = "Complete"

    df.loc[
        ~df["has_complete_route"],
        "data_quality_status",
    ] = "Incomplete route"

    df.loc[
        df["has_complete_route"]
        & ~df["has_known_operator"],
        "data_quality_status",
    ] = "Unknown operator"

    df.loc[
        df["has_complete_route"]
        & df["has_known_operator"]
        & ~df["has_known_callsign"],
        "data_quality_status",
    ] = "Missing callsign"

    # --------------------------------------------------------
    # Flight ID
    # --------------------------------------------------------

    df["flight_id"] = (
        df["id"]
        .astype(str)
    )

    # --------------------------------------------------------
    # Source metadata
    # --------------------------------------------------------

    df["source"] = "OPDI"

    df["source_version"] = (
        df["version"]
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # Filter to AeroPulse airport network
    #
    # Keep flights where either:
    # - departure is one of the five German airports
    # OR
    # - arrival is one of the five German airports
    # --------------------------------------------------------

    target_mask = (
        target_departure
        | target_arrival
    )

    filtered_df = df.loc[
        target_mask
    ].copy()

    filtered_rows = len(
        filtered_df
    )

    # --------------------------------------------------------
    # Remove duplicate flight IDs
    # --------------------------------------------------------

    before_duplicates = len(
        filtered_df
    )

    filtered_df = (
        filtered_df
        .drop_duplicates(
            subset=["flight_id"],
            keep="first",
        )
    )

    duplicates_removed = (
        before_duplicates
        - len(filtered_df)
    )

    # --------------------------------------------------------
    # Select final columns
    # --------------------------------------------------------

    filtered_df = filtered_df[
        OUTPUT_COLUMNS
    ].copy()

    # --------------------------------------------------------
    # File statistics
    # --------------------------------------------------------

    statistics = {

        "file": file.name,

        "original_rows": original_rows,

        "target_airport_rows": filtered_rows,

        "duplicates_removed": duplicates_removed,

        "final_rows": len(
            filtered_df
        ),

        "known_operator_rows": int(
            filtered_df[
                "has_known_operator"
            ].sum()
        ),

        "target_airline_rows": int(
            filtered_df[
                "is_target_airline"
            ].sum()
        ),

        "complete_route_rows": int(
            filtered_df[
                "has_complete_route"
            ].sum()
        ),

        "missing_route_rows": int(
            (
                ~filtered_df[
                    "has_complete_route"
                ]
            ).sum()
        ),
    }

    return (
        filtered_df,
        statistics,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print_header(
        "AeroPulse — OPDI Flight Transformation"
    )

    print(
        f"Project root:\n{PROJECT_ROOT}"
    )

    print()

    print(
        f"Raw OPDI directory:\n{RAW_DIR}"
    )

    print()

    print(
        f"Processed output directory:\n"
        f"{PROCESSED_DIR}"
    )

    print()

    print(
        f"Historical window:\n"
        f"{START_DATE.date()} "
        f"to "
        f"{END_DATE.date()}"
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Find monthly files
    # --------------------------------------------------------

    print_header(
        "1. Finding OPDI monthly files"
    )

    files = sorted(
        RAW_DIR.glob(
            "flight_list_*.parquet"
        )
    )

    print(
        f"Files found: {len(files)}"
    )

    if len(files) != 12:

        print()

        print(
            "WARNING:"
        )

        print(
            "Expected 12 monthly files "
            "for the AeroPulse rolling "
            "12-month window."
        )

        print()

        for file in files:

            print(
                f"  {file.name}"
            )

        print()

        response = input(
            "Continue anyway? "
            "Type YES to continue: "
        )

        if response.strip().upper() != "YES":

            print(
                "Transformation cancelled."
            )

            return 1

    # --------------------------------------------------------
    # Process files
    # --------------------------------------------------------

    print_header(
        "2. Transforming monthly files"
    )

    start_time = time.time()

    transformed_frames = []

    statistics = []

    for file in files:

        try:

            transformed_df, file_stats = (
                transform_file(file)
            )

            transformed_frames.append(
                transformed_df
            )

            statistics.append(
                file_stats
            )

            print(
                f"  Final rows: "
                f"{file_stats['final_rows']:,}"
            )

        except Exception as error:

            print()

            print(
                f"ERROR processing "
                f"{file.name}"
            )

            print(
                f"Details: {error}"
            )

            return 1

    # --------------------------------------------------------
    # Combine monthly results
    # --------------------------------------------------------

    print_header(
        "3. Combining transformed data"
    )

    final_df = pd.concat(
        transformed_frames,
        ignore_index=True,
    )

    print(
        f"Combined rows: "
        f"{len(final_df):,}"
    )

    # --------------------------------------------------------
    # Validate date window
    # --------------------------------------------------------

    print_header(
        "4. Validating historical window"
    )

    date_min = final_df[
        "flight_date"
    ].min()

    date_max = final_df[
        "flight_date"
    ].max()

    print(
        f"Minimum flight date: "
        f"{date_min}"
    )

    print(
        f"Maximum flight date: "
        f"{date_max}"
    )

    outside_window = (
        (final_df["flight_date"] < START_DATE)
        | (final_df["flight_date"] > END_DATE)
    )

    outside_count = int(
        outside_window.sum()
    )

    print(
        f"Records outside requested "
        f"window: {outside_count:,}"
    )

    if outside_count > 0:

        print(
            "Removing records outside "
            "the requested window."
        )

        final_df = final_df.loc[
            ~outside_window
        ].copy()

    # --------------------------------------------------------
    # Global duplicate check
    # --------------------------------------------------------

    print_header(
        "5. Global duplicate check"
    )

    before = len(final_df)

    final_df = (
        final_df
        .drop_duplicates(
            subset=["flight_id"],
            keep="first",
        )
        .copy()
    )

    duplicates_removed = (
        before
        - len(final_df)
    )

    print(
        f"Duplicate records removed: "
        f"{duplicates_removed:,}"
    )

    print(
        f"Final records: "
        f"{len(final_df):,}"
    )

    # --------------------------------------------------------
    # Target airport summary
    # --------------------------------------------------------

    print_header(
        "6. Target airport summary"
    )

    airport_rows = []

    for icao, information in (
        TARGET_AIRPORTS.items()
    ):

        departures = int(
            (
                final_df[
                    "departure_airport_icao"
                ]
                == icao
            ).sum()
        )

        arrivals = int(
            (
                final_df[
                    "arrival_airport_icao"
                ]
                == icao
            ).sum()
        )

        airport_rows.append(
            {
                "icao": icao,
                "iata": information["iata"],
                "airport": information["name"],
                "departures": departures,
                "arrivals": arrivals,
                "total_activity": (
                    departures
                    + arrivals
                ),
            }
        )

    airport_summary = pd.DataFrame(
        airport_rows
    )

    print(
        airport_summary.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Target airline summary
    # --------------------------------------------------------

    print_header(
        "7. Target airline summary"
    )

    airline_rows = []

    for code, information in (
        TARGET_AIRLINES.items()
    ):

        count = int(
            (
                final_df[
                    "icao_operator"
                ]
                == code
            ).sum()
        )

        airline_rows.append(
            {
                "icao_operator": code,
                "airline": information[
                    "airline_name"
                ],
                "category": information[
                    "airline_category"
                ],
                "observed_records": count,
            }
        )

    airline_summary = pd.DataFrame(
        airline_rows
    )

    print(
        airline_summary.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Data quality summary
    # --------------------------------------------------------

    print_header(
        "8. Data quality summary"
    )

    total_rows = len(final_df)

    known_operator = int(
        final_df[
            "has_known_operator"
        ].sum()
    )

    complete_routes = int(
        final_df[
            "has_complete_route"
        ].sum()
    )

    target_airlines = int(
        final_df[
            "is_target_airline"
        ].sum()
    )

    known_callsigns = int(
        final_df[
            "has_known_callsign"
        ].sum()
    )

    print(
        f"Final records: "
        f"{total_rows:,}"
    )

    if total_rows > 0:

        print(
            f"Known operator: "
            f"{known_operator:,} "
            f"({known_operator / total_rows * 100:.1f}%)"
        )

        print(
            f"Complete route: "
            f"{complete_routes:,} "
            f"({complete_routes / total_rows * 100:.1f}%)"
        )

        print(
            f"Known callsign: "
            f"{known_callsigns:,} "
            f"({known_callsigns / total_rows * 100:.1f}%)"
        )

        print(
            f"Target airline records: "
            f"{target_airlines:,} "
            f"({target_airlines / total_rows * 100:.1f}%)"
        )

    # --------------------------------------------------------
    # Save processed Parquet
    # --------------------------------------------------------

    print_header(
        "9. Saving processed dataset"
    )

    print(
        f"Writing:\n{OUTPUT_FILE}"
    )

    final_df.to_parquet(
        OUTPUT_FILE,
        engine="pyarrow",
        index=False,
    )

    output_size_mb = (
        OUTPUT_FILE.stat().st_size
        / (1024 * 1024)
    )

    print(
        "Saved successfully."
    )

    print(
        f"Output size: "
        f"{output_size_mb:.2f} MB"
    )

    # --------------------------------------------------------
    # Save quality report
    # --------------------------------------------------------

    print_header(
        "10. Saving quality report"
    )

    quality_df = pd.DataFrame(
        statistics
    )

    quality_df.to_csv(
        QUALITY_REPORT_FILE,
        index=False,
    )

    print(
        f"Saved:\n{QUALITY_REPORT_FILE}"
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    elapsed = (
        time.time()
        - start_time
    )

    print_header(
        "11. Transformation complete"
    )

    print(
        "SUCCESS"
    )

    print()

    print(
        f"Processing time: "
        f"{elapsed:.1f} seconds"
    )

    print()

    print(
        f"Final dataset rows: "
        f"{len(final_df):,}"
    )

    print()

    print(
        "Processed dataset:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "Quality report:"
    )

    print(
        QUALITY_REPORT_FILE
    )

    print()

    print(
        "Raw OPDI files were not modified."
    )

    print()

    print(
        "The processed dataset is now ready "
        "for the next validation step."
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )