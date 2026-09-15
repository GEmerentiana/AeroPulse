"""
AeroPulse — OpenSky Flights Parquet Inspector

Purpose
-------
Inspect one OpenSky historical flights Parquet file before
building the production ingestion pipeline.

This script:
    1. Finds the downloaded Parquet file
    2. Prints its schema
    3. Prints row count
    4. Shows the first records
    5. Lists null counts
    6. Displays useful values for airport/callsign fields

This is an inspection script only.
It does NOT modify the source data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pyarrow.parquet as pq


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FLIGHTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "opensky_snapshot"
    / "flights"
    / "day=1772323200"
)


# ============================================================
# HELPERS
# ============================================================

def print_header(title: str) -> None:
    """Print a readable section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print_header("AeroPulse — OpenSky Flights Inspector")

    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Flights directory: {FLIGHTS_DIR}")

    # --------------------------------------------------------
    # 1. Check directory
    # --------------------------------------------------------

    print_header("1. Checking downloaded files")

    if not FLIGHTS_DIR.exists():
        print("ERROR: Flights directory does not exist.")
        print()
        print("Expected:")
        print(FLIGHTS_DIR)
        return 1

    parquet_files = sorted(FLIGHTS_DIR.glob("*.parquet"))

    if not parquet_files:
        print("ERROR: No Parquet files found.")
        print()
        print("Expected a file ending with:")
        print(".snappy.parquet")
        return 1

    print(f"Parquet files found: {len(parquet_files)}")

    for file in parquet_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {file.name}")
        print(f"    Size: {size_mb:.2f} MB")

    # --------------------------------------------------------
    # 2. Inspect first file
    # --------------------------------------------------------

    file_path = parquet_files[0]

    print_header("2. Inspecting first Parquet file")

    print(f"File: {file_path.name}")

    try:
        parquet_file = pq.ParquetFile(file_path)

    except Exception as error:
        print("ERROR: Could not read Parquet file.")
        print(f"Details: {error}")
        return 1

    print(f"Row groups: {parquet_file.num_row_groups}")
    print(f"Rows: {parquet_file.metadata.num_rows}")

    # --------------------------------------------------------
    # 3. Schema
    # --------------------------------------------------------

    print_header("3. OpenSky flight schema")

    schema = parquet_file.schema_arrow

    for field in schema:
        print(f"  {field.name}: {field.type}")

    # --------------------------------------------------------
    # 4. Read sample
    # --------------------------------------------------------

    print_header("4. First five records")

    try:
        table = pq.read_table(
            file_path,
            use_threads=True,
        )

        dataframe = table.to_pandas()

    except Exception as error:
        print("ERROR: Could not convert Parquet to pandas.")
        print(f"Details: {error}")
        return 1

    print(dataframe.head(5).to_string())

    # --------------------------------------------------------
    # 5. Column names
    # --------------------------------------------------------

    print_header("5. Column names")

    for index, column in enumerate(dataframe.columns, start=1):
        print(f"{index:2}. {column}")

    # --------------------------------------------------------
    # 6. Null counts
    # --------------------------------------------------------

    print_header("6. Null counts")

    null_counts = dataframe.isna().sum()

    for column, count in null_counts.items():
        percentage = (
            count / len(dataframe) * 100
            if len(dataframe) > 0
            else 0
        )

        print(
            f"{column}: "
            f"{count:,} null "
            f"({percentage:.1f}%)"
        )

    # --------------------------------------------------------
    # 7. Basic data types
    # --------------------------------------------------------

    print_header("7. Pandas data types")

    print(dataframe.dtypes.to_string())

    # --------------------------------------------------------
    # 8. Dataset summary
    # --------------------------------------------------------

    print_header("8. Dataset summary")

    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")

    # --------------------------------------------------------
    # 9. Potential aviation identifiers
    # --------------------------------------------------------

    print_header("9. Potential aviation identifier fields")

    interesting_terms = [
        "icao",
        "callsign",
        "airport",
        "origin",
        "destination",
        "firstseen",
        "lastseen",
        "departure",
        "arrival",
        "airline",
    ]

    matched_columns = []

    for column in dataframe.columns:

        column_lower = column.lower()

        if any(term in column_lower for term in interesting_terms):
            matched_columns.append(column)

    if matched_columns:

        for column in matched_columns:
            print(f"  {column}")

    else:
        print("No obvious aviation identifier columns found.")

    # --------------------------------------------------------
    # 10. Final result
    # --------------------------------------------------------

    print_header("10. Inspection result")

    print("SUCCESS")
    print()
    print("The OpenSky flights Parquet file can be read.")
    print()
    print("Next step:")
    print("Use the observed schema to design the production")
    print("AeroPulse flight ingestion and transformation process.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())