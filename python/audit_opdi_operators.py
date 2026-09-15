"""
AeroPulse — OPDI Operator Audit

Purpose
-------
Audit ICAO operator codes across the complete
12-month OPDI historical dataset.

Historical window:
August 2025 through July 2026

This script does NOT modify raw data.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OPDI_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "opdi"
)


# ============================================================
# TARGET AIRLINES
# ============================================================

TARGET_OPERATORS = {
    "DLH": "Lufthansa",
    "AFR": "Air France",
    "KLM": "KLM",
    "BAW": "British Airways",
    "RYR": "Ryanair",
    "EZY": "easyJet",
    "WZZ": "Wizz Air",
    "EWG": "Eurowings",
}


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

    print_header(
        "AeroPulse — OPDI Operator Audit"
    )

    print(
        f"OPDI directory:\n{OPDI_DIR}"
    )

    files = sorted(
        OPDI_DIR.glob(
            "flight_list_*.parquet"
        )
    )

    print()

    print(
        f"Parquet files found: {len(files)}"
    )

    if len(files) == 0:

        print()
        print(
            "ERROR: No OPDI Parquet files found."
        )

        return 1

    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------

    operator_counts = {}

    monthly_target_counts = []

    total_rows = 0

    total_operator_known = 0

    total_operator_unknown = 0

    # --------------------------------------------------------
    # Process monthly files
    # --------------------------------------------------------

    for file in files:

        print()
        print(
            f"Processing: {file.name}"
        )

        df = pd.read_parquet(
            file,
            columns=[
                "dof",
                "icao_operator",
                "flt_id",
            ],
        )

        rows = len(df)

        total_rows += rows

        # ----------------------------------------------------
        # Normalize operator
        # ----------------------------------------------------

        operators = (
            df["icao_operator"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        known = (
            operators != ""
        )

        total_operator_known += int(
            known.sum()
        )

        total_operator_unknown += int(
            (~known).sum()
        )

        # ----------------------------------------------------
        # Overall operator counts
        # ----------------------------------------------------

        counts = (
            operators[
                operators != ""
            ]
            .value_counts()
        )

        for operator, count in counts.items():

            operator_counts[operator] = (
                operator_counts.get(
                    operator,
                    0,
                )
                + int(count)
            )

        # ----------------------------------------------------
        # Target airline counts
        # ----------------------------------------------------

        monthly_result = {
            "file": file.name,
            "rows": rows,
        }

        for code, airline in TARGET_OPERATORS.items():

            count = int(
                (
                    operators == code
                ).sum()
            )

            monthly_result[
                code
            ] = count

        monthly_target_counts.append(
            monthly_result
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_header(
        "1. Dataset summary"
    )

    print(
        f"Total rows: {total_rows:,}"
    )

    print(
        f"Operator known: "
        f"{total_operator_known:,}"
    )

    print(
        f"Operator missing: "
        f"{total_operator_unknown:,}"
    )

    known_percentage = (
        total_operator_known
        / total_rows
        * 100
    )

    unknown_percentage = (
        total_operator_unknown
        / total_rows
        * 100
    )

    print(
        f"Operator known: "
        f"{known_percentage:.1f}%"
    )

    print(
        f"Operator missing: "
        f"{unknown_percentage:.1f}%"
    )

    # --------------------------------------------------------
    # Target airlines
    # --------------------------------------------------------

    print_header(
        "2. Target airline audit"
    )

    print(
        f"{'Code':<8}"
        f"{'Airline':<20}"
        f"{'Flights':>15}"
    )

    print("-" * 45)

    for code, airline in TARGET_OPERATORS.items():

        count = operator_counts.get(
            code,
            0,
        )

        print(
            f"{code:<8}"
            f"{airline:<20}"
            f"{count:>15,}"
        )

    # --------------------------------------------------------
    # Top operators
    # --------------------------------------------------------

    print_header(
        "3. Top 30 operator codes"
    )

    top_operators = sorted(
        operator_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:30]

    print(
        f"{'Rank':<6}"
        f"{'ICAO':<10}"
        f"{'Flights':>15}"
    )

    print("-" * 35)

    for rank, (
        operator,
        count,
    ) in enumerate(
        top_operators,
        start=1,
    ):

        print(
            f"{rank:<6}"
            f"{operator:<10}"
            f"{count:>15,}"
        )

    # --------------------------------------------------------
    # Monthly target airline counts
    # --------------------------------------------------------

    print_header(
        "4. Target airlines by month"
    )

    monthly_df = pd.DataFrame(
        monthly_target_counts
    )

    print(
        monthly_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print_header(
        "5. Audit result"
    )

    print(
        "SUCCESS"
    )

    print()
    print(
        "The OPDI operator field has been audited "
        "across the historical dataset."
    )

    print()
    print(
        "Next step:"
    )

    print(
        "Use the audit results to design "
        "the airline enrichment rules."
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )