"""
AeroPulse — OPDI Flight List Inspector

Purpose
-------
Inspect one monthly OPDI Flight List Parquet file before
building the production historical-flight pipeline.

Source:
Open Performance Data Initiative (OPDI)
https://www.opdi.aero/

This script does NOT modify the downloaded data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OPDI_DIR = PROJECT_ROOT / "data" / "raw" / "opdi"

TEST_FILE = OPDI_DIR / "flight_list_202508.parquet"


# ============================================================
# HELPERS
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print_header("AeroPulse — OPDI Flight List Inspector")

    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"OPDI directory: {OPDI_DIR}")
    print(f"Test file: {TEST_FILE}")

    # --------------------------------------------------------
    # 1. Check file
    # --------------------------------------------------------

    print_header("1. Checking OPDI file")

    if not TEST_FILE.exists():

        print("ERROR: OPDI Parquet file was not found.")
        print()
        print("Expected:")
        print(TEST_FILE)
        print()
        print("Download flight_list_202508.parquet first.")

        return 1

    size_mb = TEST_FILE.stat().st_size / (1024 * 1024)

    print("File found.")
    print(f"Size: {size_mb:.2f} MB")

    # --------------------------------------------------------
    # 2. Read file
    # --------------------------------------------------------

    print_header("2. Reading OPDI Flight List")

    try:

        df = pd.read_parquet(
            TEST_FILE,
            engine="pyarrow",
        )

    except Exception as error:

        print("ERROR: Could not read Parquet file.")
        print(f"Details: {error}")

        return 1

    print("SUCCESS: File loaded.")

    # --------------------------------------------------------
    # 3. Dataset size
    # --------------------------------------------------------

    print_header("3. Dataset size")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------------
    # 4. Columns
    # --------------------------------------------------------

    print_header("4. Columns")

    for number, column in enumerate(df.columns, start=1):

        print(f"{number:2}. {column}")

    # --------------------------------------------------------
    # 5. Data types
    # --------------------------------------------------------

    print_header("5. Data types")

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # 6. First records
    # --------------------------------------------------------

    print_header("6. First five records")

    print(
        df.head(5).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # 7. Null counts
    # --------------------------------------------------------

    print_header("7. Null counts")

    null_counts = df.isna().sum()

    for column, count in null_counts.items():

        percentage = (
            count / len(df) * 100
            if len(df) > 0
            else 0
        )

        print(
            f"{column}: "
            f"{count:,} null "
            f"({percentage:.1f}%)"
        )

    # --------------------------------------------------------
    # 8. Potential airport fields
    # --------------------------------------------------------

    print_header("8. Airport-related fields")

    airport_terms = [
        "adep",
        "ades",
        "airport",
        "origin",
        "destination",
    ]

    airport_columns = [
        column
        for column in df.columns
        if any(
            term in column.lower()
            for term in airport_terms
        )
    ]

    if airport_columns:

        for column in airport_columns:
            print(f"  {column}")

    else:

        print("No airport-related columns detected.")

    # --------------------------------------------------------
    # 9. Potential airline/operator fields
    # --------------------------------------------------------

    print_header("9. Airline/operator-related fields")

    airline_terms = [
        "airline",
        "operator",
        "carrier",
        "icao_operator",
        "callsign",
        "flt_id",
    ]

    airline_columns = [
        column
        for column in df.columns
        if any(
            term in column.lower()
            for term in airline_terms
        )
    ]

    if airline_columns:

        for column in airline_columns:
            print(f"  {column}")

    else:

        print("No obvious airline/operator fields detected.")

    # --------------------------------------------------------
    # 10. Date fields
    # --------------------------------------------------------

    print_header("10. Date/time-related fields")

    date_terms = [
        "date",
        "dof",
        "first_seen",
        "last_seen",
        "time",
    ]

    date_columns = [
        column
        for column in df.columns
        if any(
            term in column.lower()
            for term in date_terms
        )
    ]

    if date_columns:

        for column in date_columns:
            print(f"  {column}")

    else:

        print("No obvious date/time fields detected.")

    # --------------------------------------------------------
    # 11. Target airport test
    # --------------------------------------------------------

    print_header("11. Target airport test")

    target_airports = {
        "EDDF": "FRA",
        "EDDM": "MUC",
        "EDDB": "BER",
        "EDDL": "DUS",
        "EDDH": "HAM",
    }

    for column in ["adep", "ades", "ADEP", "ADES"]:

        if column not in df.columns:
            continue

        print(f"Testing column: {column}")

        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.upper()
        )

        for icao, iata in target_airports.items():

            count = (values == icao).sum()

            print(
                f"  {iata} ({icao}): "
                f"{count:,}"
            )

    # --------------------------------------------------------
    # 12. Date range
    # --------------------------------------------------------

    print_header("12. Date range")

    possible_date_columns = [
        "dof",
        "DOF",
        "date",
        "flight_date",
    ]

    found_date_column = None

    for column in possible_date_columns:

        if column in df.columns:

            found_date_column = column
            break

    if found_date_column:

        dates = pd.to_datetime(
            df[found_date_column],
            errors="coerce",
        )

        print(f"Date column: {found_date_column}")
        print(f"Minimum date: {dates.min()}")
        print(f"Maximum date: {dates.max()}")

    else:

        print("No standard flight-date column found.")

    # --------------------------------------------------------
    # 13. Final result
    # --------------------------------------------------------

    print_header("13. Inspection result")

    print("SUCCESS")
    print()
    print("The OPDI monthly Flight List can be read.")
    print()
    print("Next step:")
    print("Design the AeroPulse OPDI ingestion pipeline")
    print("for the full rolling 12-month window.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())