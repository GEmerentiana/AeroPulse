"""
AeroPulse — OPDI Test Downloader

Downloads one OPDI monthly Flight List file and
shows download progress.

Test file:
August 2025
"""

from pathlib import Path
import requests
import sys
import time


# ============================================================
# SETTINGS
# ============================================================

URL = (
    "https://www.eurocontrol.int/performance/data/download/"
    "OPDI/v002/flight_list/flight_list_202508.parquet"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "opdi"

OUTPUT_FILE = OUTPUT_DIR / "flight_list_202508.parquet"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("AeroPulse — OPDI Test Downloader")
    print("=" * 70)

    print()
    print(f"Source:")
    print(URL)

    print()
    print(f"Destination:")
    print(OUTPUT_FILE)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    print()
    print("Connecting to OPDI...")
    print()

    try:

        with requests.get(
            URL,
            stream=True,
            timeout=60
        ) as response:

            response.raise_for_status()

            total_size = int(
                response.headers.get(
                    "content-length",
                    0
                )
            )

            print(
                f"HTTP status: {response.status_code}"
            )

            if total_size:
                print(
                    f"File size: "
                    f"{total_size / (1024 * 1024):.2f} MB"
                )
            else:
                print(
                    "File size: unknown"
                )

            print()
            print("Downloading...")
            print()

            downloaded = 0

            start_time = time.time()

            with open(
                OUTPUT_FILE,
                "wb"
            ) as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if not chunk:
                        continue

                    file.write(chunk)

                    downloaded += len(chunk)

                    elapsed = (
                        time.time() - start_time
                    )

                    speed = (
                        downloaded / elapsed
                        if elapsed > 0
                        else 0
                    )

                    if total_size:

                        percent = (
                            downloaded
                            / total_size
                            * 100
                        )

                        downloaded_mb = (
                            downloaded
                            / (1024 * 1024)
                        )

                        total_mb = (
                            total_size
                            / (1024 * 1024)
                        )

                        speed_mbps = (
                            speed
                            / (1024 * 1024)
                        )

                        print(
                            f"\r"
                            f"{percent:6.2f}% | "
                            f"{downloaded_mb:,.1f} / "
                            f"{total_mb:,.1f} MB | "
                            f"{speed_mbps:,.2f} MB/s",
                            end="",
                            flush=True
                        )

                    else:

                        downloaded_mb = (
                            downloaded
                            / (1024 * 1024)
                        )

                        print(
                            f"\r"
                            f"{downloaded_mb:,.1f} MB",
                            end="",
                            flush=True
                        )

            print()
            print()
            print("=" * 70)
            print("DOWNLOAD COMPLETE")
            print("=" * 70)

            print()
            print(f"Saved to:")
            print(OUTPUT_FILE)

            print()

            if OUTPUT_FILE.exists():

                final_size = (
                    OUTPUT_FILE.stat().st_size
                    / (1024 * 1024)
                )

                print(
                    f"Final file size: "
                    f"{final_size:,.2f} MB"
                )

            print()
            print("Next step:")
            print(
                "python python\\inspect_opdi_flights.py"
            )

    except requests.exceptions.RequestException as error:

        print()
        print("=" * 70)
        print("DOWNLOAD FAILED")
        print("=" * 70)

        print()
        print(f"Error: {error}")

        if OUTPUT_FILE.exists():

            print()
            print(
                "A partial file may have been created:"
            )

            print(OUTPUT_FILE)

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())