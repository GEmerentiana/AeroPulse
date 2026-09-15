"""
AeroPulse — OpenSky Historical Flight Endpoint Test

Purpose
-------
Test whether OpenSky's historical flight endpoints can return
completed observed flights for AeroPulse.

This is a source-validation script only.
It does NOT create the production flight dataset.

Important:
OpenSky historical flights are reconstructed from observed
aircraft tracking data. They are NOT commercial schedule data.

The test uses:
    /api/flights/arrival
    /api/flights/departure

Target airport:
    FRA - Frankfurt Airport

Source:
https://opensky-network.org/
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# OPEN SKY API
# ============================================================

ARRIVAL_URL = "https://opensky-network.org/api/flights/arrival"
DEPARTURE_URL = "https://opensky-network.org/api/flights/departure"


# ============================================================
# TEST CONFIGURATION
# ============================================================

AIRPORT = "EDDF"  # Frankfurt Airport ICAO code

# We test yesterday because OpenSky explains that historical
# flight information is generated after the day has finished.
TEST_DATE = datetime.now(timezone.utc).date() - timedelta(days=1)

START_OF_DAY = datetime.combine(
    TEST_DATE,
    datetime.min.time(),
    tzinfo=timezone.utc,
)

END_OF_DAY = START_OF_DAY + timedelta(days=1) - timedelta(seconds=1)

BEGIN_UNIX = int(START_OF_DAY.timestamp())
END_UNIX = int(END_OF_DAY.timestamp())


# ============================================================
# HELPERS
# ============================================================

def print_header(title: str) -> None:
    """Print a readable section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def describe_http_error(response: requests.Response) -> None:
    """Print useful information about an HTTP error."""

    print()
    print("OpenSky API request failed.")
    print(f"HTTP status: {response.status_code}")

    if response.status_code == 400:
        print("Bad request. Check endpoint parameters.")

    elif response.status_code == 401:
        print("Authentication is required for this request.")

    elif response.status_code == 403:
        print("Access was denied by OpenSky.")

    elif response.status_code == 404:
        print("Endpoint or resource was not found.")

    elif response.status_code == 429:
        print("Rate limit reached. Please wait before retrying.")

    elif response.status_code >= 500:
        print("OpenSky server returned a server-side error.")

    try:
        print(f"Response body: {response.text[:500]}")
    except Exception:
        pass


def request_flights(
    url: str,
    airport: str,
    begin: int,
    end: int,
) -> list:
    """
    Request historical flights from OpenSky.
    """

    params = {
        "airport": airport,
        "begin": begin,
        "end": end,
    }

    print()
    print(f"Requesting: {url}")
    print(f"Parameters: {params}")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=60,
        )
    except requests.Timeout as error:
        raise RuntimeError(
            f"Request timed out after 60 seconds: {error}"
        ) from error

    except requests.ConnectionError as error:
        raise RuntimeError(
            f"Connection error while contacting OpenSky: {error}"
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"Unexpected request error: {error}"
        ) from error

    if response.status_code != 200:
        describe_http_error(response)
        response.raise_for_status()

    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError(
            "OpenSky returned a response that is not valid JSON."
        ) from error

    if not isinstance(data, list):
        raise RuntimeError(
            f"Unexpected response type: {type(data).__name__}"
        )

    return data


def inspect_flights(
    flight_type: str,
    flights: list,
) -> None:
    """Print a compact inspection of historical flight records."""

    print()
    print(f"{flight_type} flights returned: {len(flights)}")

    if not flights:
        print("No flights returned.")
        return

    print()
    print(f"First {flight_type.lower()} flight:")

    first = flights[0]

    print(f"  Raw record length: {len(first)}")
    print(f"  Raw record: {first}")

    print()
    print("First several records:")

    for index, flight in enumerate(flights[:5], start=1):
        print(f"  {index}: {flight}")


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print_header("AeroPulse — OpenSky Historical Flight Test")

    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Test date UTC: {TEST_DATE}")
    print(f"Airport ICAO: {AIRPORT}")
    print(f"Begin Unix timestamp: {BEGIN_UNIX}")
    print(f"End Unix timestamp: {END_UNIX}")

    # --------------------------------------------------------
    # 1. Test historical arrivals
    # --------------------------------------------------------

    print_header("1. Testing historical arrivals")

    try:

        arrivals = request_flights(
            url=ARRIVAL_URL,
            airport=AIRPORT,
            begin=BEGIN_UNIX,
            end=END_UNIX,
        )

        inspect_flights(
            flight_type="Arrival",
            flights=arrivals,
        )

    except Exception as error:

        print()
        print("ERROR: Historical arrival request failed.")
        print(f"Details: {error}")

        arrivals = None

    # --------------------------------------------------------
    # 2. Test historical departures
    # --------------------------------------------------------

    print_header("2. Testing historical departures")

    try:

        departures = request_flights(
            url=DEPARTURE_URL,
            airport=AIRPORT,
            begin=BEGIN_UNIX,
            end=END_UNIX,
        )

        inspect_flights(
            flight_type="Departure",
            flights=departures,
        )

    except Exception as error:

        print()
        print("ERROR: Historical departure request failed.")
        print(f"Details: {error}")

        departures = None

    # --------------------------------------------------------
    # 3. Initial assessment
    # --------------------------------------------------------

    print_header("3. Historical source assessment")

    if arrivals is not None:
        print("Arrival endpoint: RESPONDED")

    else:
        print("Arrival endpoint: FAILED")

    if departures is not None:
        print("Departure endpoint: RESPONDED")

    else:
        print("Departure endpoint: FAILED")

    print()
    print("Important interpretation:")
    print()
    print("OpenSky historical flight records represent")
    print("observed/reconstructed flights from tracking data.")
    print()
    print("They should NOT be interpreted as:")
    print("  - Scheduled commercial flights")
    print("  - Confirmed cancellations")
    print("  - Passenger demand")
    print("  - Ticket sales")
    print("  - Guaranteed airline schedules")
    print("  - Commercial on-time performance")
    print()

    # --------------------------------------------------------
    # 4. Final result
    # --------------------------------------------------------

    print_header("4. Test result")

    if arrivals is not None and departures is not None:

        print("SUCCESS")
        print()
        print("OpenSky historical arrival and departure endpoints")
        print("responded successfully for Frankfurt.")
        print()
        print("Next step:")
        print("Inspect the returned fields and determine the")
        print("production observed-flight schema.")

        return 0

    if arrivals is not None or departures is not None:

        print("PARTIAL SUCCESS")
        print()
        print("At least one historical endpoint responded.")
        print("We need to investigate the failed endpoint before")
        print("building the production pipeline.")

        return 0

    print("FAILED")
    print()
    print("Neither historical endpoint returned successfully.")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())