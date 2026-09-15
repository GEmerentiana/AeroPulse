"""
AeroPulse — OpenSky API Source Test

Purpose
-------
Test connectivity to the OpenSky REST API and inspect the state-vector
fields returned for the five target German airports.

This is a source-validation script only.
It does NOT create the production flight dataset.

Target airports:
    FRA - Frankfurt
    MUC - Munich
    BER - Berlin Brandenburg
    DUS - Düsseldorf
    HAM - Hamburg

Important:
OpenSky state vectors represent observed aircraft tracking data.
They do not directly provide commercial schedule information,
passenger counts, ticket prices, or confirmed cancellations.

Source:
https://opensky-network.org/
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


# ============================================================
# OPEN SKY API
# ============================================================

OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"


# ============================================================
# TARGET AIRPORTS
# Bounding boxes are intentionally small test areas around
# each airport. They are NOT airport boundaries.
# ============================================================

AIRPORTS = {
    "FRA": {
        "name": "Frankfurt Airport",
        "lat_min": 50.00,
        "lat_max": 50.15,
        "lon_min": 8.40,
        "lon_max": 8.70,
    },
    "MUC": {
        "name": "Munich Airport",
        "lat_min": 48.25,
        "lat_max": 48.45,
        "lon_min": 11.35,
        "lon_max": 11.75,
    },
    "BER": {
        "name": "Berlin Brandenburg Airport",
        "lat_min": 52.30,
        "lat_max": 52.65,
        "lon_min": 13.30,
        "lon_max": 13.70,
    },
    "DUS": {
        "name": "Dusseldorf Airport",
        "lat_min": 51.15,
        "lat_max": 51.35,
        "lon_min": 6.60,
        "lon_max": 6.95,
    },
    "HAM": {
        "name": "Hamburg Airport",
        "lat_min": 53.45,
        "lat_max": 53.75,
        "lon_min": 9.85,
        "lon_max": 10.15,
    },
}


# ============================================================
# EXPECTED STATE VECTOR FIELDS
# ============================================================

EXPECTED_FIELDS = [
    "icao24",
    "callsign",
    "origin_country",
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "true_track",
    "vertical_rate",
    "sensors",
    "geo_altitude",
    "squawk",
    "spi",
    "position_source",
]


# ============================================================
# HELPERS
# ============================================================

def print_header(title: str) -> None:
    """Print a readable section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def validate_response(response: requests.Response) -> None:
    """Raise a useful error for unsuccessful HTTP responses."""
    if response.status_code == 200:
        return

    print()
    print("OpenSky API request failed.")
    print(f"HTTP status: {response.status_code}")

    if response.status_code == 401:
        print("Authentication is required for this request.")
    elif response.status_code == 403:
        print("Access was denied by OpenSky.")
    elif response.status_code == 429:
        print("Rate limit reached. Please wait before trying again.")

    response.raise_for_status()


def request_states(
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> dict:
    """
    Request current aircraft states inside a geographic bounding box.
    """

    params = {
        "lamin": lat_min,
        "lamax": lat_max,
        "lomin": lon_min,
        "lomax": lon_max,
    }

    print(f"Requesting: {OPENSKY_STATES_URL}")
    print(f"Bounding box: {params}")

    response = requests.get(
        OPENSKY_STATES_URL,
        params=params,
        timeout=30,
    )

    validate_response(response)

    return response.json()


def inspect_states(airport_code: str, data: dict) -> None:
    """Print a compact inspection of returned aircraft states."""

    states = data.get("states") or []

    print(f"\nAirport: {airport_code}")
    print(f"Aircraft states returned: {len(states)}")

    if not states:
        print("No aircraft were returned for this test area.")
        return

    print("\nFirst aircraft record:")

    first_state = states[0]

    for index, value in enumerate(first_state):
        if index < len(EXPECTED_FIELDS):
            field_name = EXPECTED_FIELDS[index]
        else:
            field_name = f"unknown_field_{index}"

        print(f"  {field_name}: {value}")

    print("\nExample callsigns:")

    callsigns = []

    for state in states:
        if len(state) > 1 and state[1]:
            callsign = str(state[1]).strip()

            if callsign:
                callsigns.append(callsign)

    for callsign in callsigns[:10]:
        print(f"  {callsign}")

    if not callsigns:
        print("  No callsigns returned.")


# ============================================================
# MAIN TEST
# ============================================================

def main() -> int:
    print_header("AeroPulse — OpenSky API Test")

    print(f"Test time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root: {PROJECT_ROOT}")

    # --------------------------------------------------------
    # 1. Basic connectivity test
    # --------------------------------------------------------

    print_header("1. Testing OpenSky API connectivity")

    try:
        response = requests.get(
            OPENSKY_STATES_URL,
            params={"lamin": 50.00, "lamax": 50.15, "lomin": 8.40, "lomax": 8.70},
            timeout=30,
        )

        validate_response(response)

        print("SUCCESS: OpenSky API is reachable.")
        print(f"HTTP status: {response.status_code}")

    except requests.RequestException as error:
        print("ERROR: Could not connect to OpenSky.")
        print(f"Details: {error}")
        return 1

    # --------------------------------------------------------
    # 2. Inspect target airports
    # --------------------------------------------------------

    print_header("2. Testing the five target airports")

    successful_airports = 0

    for airport_code, airport in AIRPORTS.items():

        try:
            data = request_states(
                lat_min=airport["lat_min"],
                lat_max=airport["lat_max"],
                lon_min=airport["lon_min"],
                lon_max=airport["lon_max"],
            )

            inspect_states(airport_code, data)

            successful_airports += 1

        except requests.RequestException as error:
            print(f"\nERROR for {airport_code}: {error}")

    # --------------------------------------------------------
    # 3. Source capability assessment
    # --------------------------------------------------------

    print_header("3. Initial source capability assessment")

    print("OpenSky state-vector data can provide observed aircraft activity.")
    print()
    print("Expected useful fields include:")
    print("  - ICAO24 aircraft identifier")
    print("  - Callsign")
    print("  - Position")
    print("  - Altitude")
    print("  - Velocity")
    print("  - Heading")
    print("  - On-ground status")
    print()
    print("Important limitations:")
    print("  - No commercial ticket price")
    print("  - No passenger count")
    print("  - No confirmed cancellation field")
    print("  - No guaranteed scheduled departure time")
    print("  - No guaranteed scheduled arrival time")
    print("  - Airline identification may require callsign/aircraft enrichment")
    print()
    print("Therefore, this test does NOT yet prove that OpenSky can")
    print("produce the final AeroPulse flight fact table.")

    # --------------------------------------------------------
    # 4. Final result
    # --------------------------------------------------------

    print_header("4. Test result")

    print(
        f"Successful airport tests: "
        f"{successful_airports}/{len(AIRPORTS)}"
    )

    if successful_airports == len(AIRPORTS):
        print()
        print("SUCCESS")
        print("OpenSky is reachable for all five test areas.")
        print()
        print("Next step:")
        print("Inspect historical/flight endpoint availability and")
        print("determine how observed flights can be reconstructed.")
        return 0

    if successful_airports > 0:
        print()
        print("PARTIAL SUCCESS")
        print("OpenSky responded, but not every airport test succeeded.")
        return 0

    print()
    print("FAILED")
    print("No airport test returned successfully.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())