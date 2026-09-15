from pathlib import Path
import requests


# ============================================================
# AeroPulse — Download OurAirports reference data
# ============================================================

BASE_URL = "https://ourairports.com/data/"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ourairports"

FILES = {
    "airports.csv": BASE_URL + "airports.csv",
    "countries.csv": BASE_URL + "countries.csv",
}


def download_file(filename: str, url: str) -> None:
    """
    Download a file from OurAirports.
    Existing files are skipped.
    """

    output_path = RAW_DIR / filename

    if output_path.exists():
        print(f"[SKIP] {filename} already exists")
        print(f"       {output_path}")
        return

    print(f"[DOWNLOAD] {filename}")
    print(f"URL: {url}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    try:
        with requests.get(
            url,
            stream=True,
            timeout=60,
            headers={
                "User-Agent": "AeroPulse aviation analytics project"
            },
        ) as response:

            response.raise_for_status()

            total_size = int(
                response.headers.get("content-length", 0)
            )

            downloaded = 0

            with open(temp_path, "wb") as f:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if not chunk:
                        continue

                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size:
                        percent = downloaded / total_size * 100

                        print(
                            f"\rProgress: {percent:6.2f}%",
                            end=""
                        )

        print()

        temp_path.replace(output_path)

        size_mb = output_path.stat().st_size / 1024 / 1024

        print(
            f"[OK] {filename} downloaded "
            f"({size_mb:.2f} MB)"
        )

    except Exception as e:

        if temp_path.exists():
            temp_path.unlink()

        print(f"[ERROR] Failed to download {filename}")
        print(f"        {e}")


def main():

    print("=" * 70)
    print("AeroPulse — OurAirports Reference Data Download")
    print("=" * 70)

    for filename, url in FILES.items():
        download_file(filename, url)

    print()
    print("=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)

    for filename in FILES:
        path = RAW_DIR / filename

        if path.exists():
            size_mb = path.stat().st_size / 1024 / 1024
            print(f"[OK]   {filename:<20} {size_mb:>8.2f} MB")
        else:
            print(f"[FAIL] {filename}")

    print()
    print("Raw files are stored in:")
    print(RAW_DIR)


if __name__ == "__main__":
    main()