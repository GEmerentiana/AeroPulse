"""
AeroPulse — OPDI Historical Flight List Downloader

Downloads the rolling 12-month OPDI Flight List dataset
for AeroPulse.

Historical window:
August 2025 through July 2026

The downloader:
- downloads monthly Parquet files
- skips files that already exist
- shows download progress
- retries failed downloads
- downloads to a temporary file first
- renames the file only after successful completion

Raw Parquet files must NOT be committed to Git.
"""

from __future__ import annotations

from pathlib import Path
from datetime import date
import sys
import time

import requests


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "opdi"
)


# ============================================================
# OPDI SOURCE
# ============================================================

BASE_URL = (
    "https://www.eurocontrol.int/performance/data/"
    "download/OPDI/v002/flight_list/"
)


# ============================================================
# HISTORICAL WINDOW
# ============================================================

START_YEAR = 2025
START_MONTH = 8

END_YEAR = 2026
END_MONTH = 7


# ============================================================
# DOWNLOAD SETTINGS
# ============================================================

CHUNK_SIZE = 1024 * 1024

REQUEST_TIMEOUT = 120

MAX_RETRIES = 3


# ============================================================
# HELPERS
# ============================================================

def print_header(title: str) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def generate_months(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
) -> list[tuple[int, int]]:

    months = []

    year = start_year
    month = start_month

    while (year, month) <= (end_year, end_month):

        months.append(
            (year, month)
        )

        month += 1

        if month == 13:

            month = 1
            year += 1

    return months


def download_file(
    year: int,
    month: int,
) -> bool:

    filename = (
        f"flight_list_{year:04d}"
        f"{month:02d}.parquet"
    )

    url = BASE_URL + filename

    output_file = OUTPUT_DIR / filename

    temporary_file = (
        OUTPUT_DIR
        / f"{filename}.part"
    )

    # --------------------------------------------------------
    # Skip existing completed file
    # --------------------------------------------------------

    if output_file.exists():

        size_mb = (
            output_file.stat().st_size
            / (1024 * 1024)
        )

        print()
        print(
            f"SKIP: {filename} already exists "
            f"({size_mb:.2f} MB)"
        )

        return True

    # --------------------------------------------------------
    # Remove incomplete temporary file
    # --------------------------------------------------------

    if temporary_file.exists():

        print(
            f"Removing incomplete file: "
            f"{temporary_file.name}"
        )

        temporary_file.unlink()

    # --------------------------------------------------------
    # Retry loop
    # --------------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        print()
        print("-" * 70)

        print(
            f"Downloading: {filename}"
        )

        print(
            f"Attempt: {attempt}/{MAX_RETRIES}"
        )

        print(
            f"URL: {url}"
        )

        try:

            with requests.get(
                url,
                stream=True,
                timeout=REQUEST_TIMEOUT,
            ) as response:

                response.raise_for_status()

                total_size = int(
                    response.headers.get(
                        "content-length",
                        0,
                    )
                )

                if total_size:

                    total_mb = (
                        total_size
                        / (1024 * 1024)
                    )

                    print(
                        f"File size: "
                        f"{total_mb:.2f} MB"
                    )

                else:

                    print(
                        "File size: unknown"
                    )

                downloaded = 0

                start_time = time.time()

                with open(
                    temporary_file,
                    "wb",
                ) as file:

                    for chunk in response.iter_content(
                        chunk_size=CHUNK_SIZE
                    ):

                        if not chunk:
                            continue

                        file.write(chunk)

                        downloaded += len(chunk)

                        elapsed = (
                            time.time()
                            - start_time
                        )

                        if elapsed > 0:

                            speed = (
                                downloaded
                                / elapsed
                            )

                        else:

                            speed = 0

                        downloaded_mb = (
                            downloaded
                            / (1024 * 1024)
                        )

                        speed_mb = (
                            speed
                            / (1024 * 1024)
                        )

                        if total_size:

                            percent = (
                                downloaded
                                / total_size
                                * 100
                            )

                            print(
                                f"\r"
                                f"{percent:6.2f}% | "
                                f"{downloaded_mb:,.1f} MB | "
                                f"{speed_mb:,.2f} MB/s",
                                end="",
                                flush=True,
                            )

                        else:

                            print(
                                f"\r"
                                f"{downloaded_mb:,.1f} MB | "
                                f"{speed_mb:,.2f} MB/s",
                                end="",
                                flush=True,
                            )

                print()

            # ------------------------------------------------
            # Verify downloaded file
            # ------------------------------------------------

            if not temporary_file.exists():

                raise RuntimeError(
                    "Temporary file was not created."
                )

            final_size = (
                temporary_file.stat().st_size
            )

            if final_size == 0:

                raise RuntimeError(
                    "Downloaded file is empty."
                )

            # ------------------------------------------------
            # Rename only after success
            # ------------------------------------------------

            temporary_file.replace(
                output_file
            )

            final_size_mb = (
                final_size
                / (1024 * 1024)
            )

            print(
                f"SUCCESS: {filename}"
            )

            print(
                f"Saved: {output_file}"
            )

            print(
                f"Size: {final_size_mb:.2f} MB"
            )

            return True

        except Exception as error:

            print()

            print(
                f"ERROR downloading {filename}:"
            )

            print(error)

            if temporary_file.exists():

                temporary_file.unlink()

            if attempt < MAX_RETRIES:

                wait_seconds = (
                    attempt * 5
                )

                print(
                    f"Retrying in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(
                    wait_seconds
                )

            else:

                print(
                    f"FAILED: {filename}"
                )

                return False

    return False


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print_header(
        "AeroPulse — OPDI Historical Downloader"
    )

    print(
        f"Project root:\n{PROJECT_ROOT}"
    )

    print()

    print(
        f"Output directory:\n{OUTPUT_DIR}"
    )

    print()

    print(
        "Historical window:"
    )

    print(
        f"{START_YEAR}-{START_MONTH:02d} "
        f"through "
        f"{END_YEAR}-{END_MONTH:02d}"
    )

    months = generate_months(
        START_YEAR,
        START_MONTH,
        END_YEAR,
        END_MONTH,
    )

    print()

    print(
        f"Monthly files required: "
        f"{len(months)}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    successful = 0
    failed = 0

    for year, month in months:

        success = download_file(
            year,
            month,
        )

        if success:

            successful += 1

        else:

            failed += 1

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_header(
        "Download Summary"
    )

    print(
        f"Successful files: {successful}"
    )

    print(
        f"Failed files:     {failed}"
    )

    print()

    print(
        "Files currently in OPDI directory:"
    )

    parquet_files = sorted(
        OUTPUT_DIR.glob(
            "flight_list_*.parquet"
        )
    )

    total_size = 0

    for file in parquet_files:

        size_mb = (
            file.stat().st_size
            / (1024 * 1024)
        )

        total_size += size_mb

        print(
            f"  {file.name:30} "
            f"{size_mb:,.2f} MB"
        )

    print()

    print(
        f"Total local Parquet size: "
        f"{total_size:,.2f} MB"
    )

    print()

    if failed == 0:

        print(
            "ALL OPDI MONTHLY FILES DOWNLOADED."
        )

        print()

        print(
            "Next step:"
        )

        print(
            "Build the OPDI transformation/"
            "filtering pipeline."
        )

        return 0

    else:

        print(
            "WARNING: Some files failed."
        )

        print(
            "Run this script again."
        )

        print(
            "Existing successful files "
            "will automatically be skipped."
        )

        return 1


if __name__ == "__main__":

    sys.exit(main())