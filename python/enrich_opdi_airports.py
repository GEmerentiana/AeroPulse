from pathlib import Path
import pandas as pd


# ============================================================
# AeroPulse — OurAirports enrichment
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opdi"
    / "aeropulse_flights.parquet"
)

AIRPORTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ourairports"
    / "airports.csv"
)

COUNTRIES_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ourairports"
    / "countries.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opdi"
)

OUTPUT_FILE = OUTPUT_DIR / "aeropulse_flights_enriched.parquet"
QUALITY_FILE = OUTPUT_DIR / "airport_enrichment_report.csv"


TARGET_AIRPORTS = {
    "EDDF": "FRA",
    "EDDM": "MUC",
    "EDDB": "BER",
    "EDDL": "DUS",
    "EDDH": "HAM",
}


EUROPE_CONTINENT = "EU"


# ============================================================
# Helper functions
# ============================================================

def clean_text(series):
    """
    Standardize text columns.
    """

    return (
        series
        .astype("string")
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
            }
        )
    )


def classify_scope(country_code, continent):
    """
    Classify airport geography.

    Germany
    Europe
    Outside Europe
    Unknown
    """

    if pd.isna(country_code) or pd.isna(continent):
        return "Unknown"

    if country_code.upper() == "DE":
        return "Germany"

    if continent.upper() == EUROPE_CONTINENT:
        return "Europe"

    return "Outside Europe"


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("AeroPulse — OurAirports Airport Enrichment")
    print("=" * 70)

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    required_files = [
        INPUT_FILE,
        AIRPORTS_FILE,
        COUNTRIES_FILE,
    ]

    for file_path in required_files:

        if not file_path.exists():

            raise FileNotFoundError(
                f"Required file not found:\n{file_path}"
            )

    # --------------------------------------------------------
    # Load OPDI flights
    # --------------------------------------------------------

    print()
    print("[1/6] Loading OPDI flight data...")

    flights = pd.read_parquet(INPUT_FILE)

    print(f"Flights loaded: {len(flights):,}")

    # --------------------------------------------------------
    # Load OurAirports
    # --------------------------------------------------------

    print()
    print("[2/6] Loading OurAirports airport reference...")

    airports = pd.read_csv(
        AIRPORTS_FILE,
        low_memory=False,
    )

    countries = pd.read_csv(
        COUNTRIES_FILE,
        low_memory=False,
    )

    print(f"Airports loaded: {len(airports):,}")
    print(f"Countries loaded: {len(countries):,}")

    # --------------------------------------------------------
    # Prepare airport reference
    # --------------------------------------------------------

    print()
    print("[3/6] Preparing airport reference...")

    required_airport_columns = [
        "ident",
        "type",
        "name",
        "latitude_deg",
        "longitude_deg",
        "iso_country",
        "iso_region",
        "municipality",
        "iata_code",
    ]

    missing_columns = [
        col
        for col in required_airport_columns
        if col not in airports.columns
    ]

    if missing_columns:

        raise ValueError(
            "OurAirports is missing required columns: "
            + ", ".join(missing_columns)
        )

    airports = airports[
        required_airport_columns
    ].copy()

    # Clean fields

    for column in [
        "ident",
        "type",
        "name",
        "iso_country",
        "iso_region",
        "municipality",
        "iata_code",
    ]:

        airports[column] = clean_text(
            airports[column]
        )

    # Keep only airports with ICAO-style identifiers
    # relevant for OPDI airport matching.

    airports["ident"] = airports["ident"].str.upper()

    airports["iata_code"] = (
        airports["iata_code"]
        .str.upper()
    )

    # --------------------------------------------------------
    # Prepare country reference
    # --------------------------------------------------------

    if "code" not in countries.columns:
        raise ValueError(
            "OurAirports countries.csv does not contain "
            "the expected 'code' column."
        )

    countries["code"] = clean_text(
        countries["code"]
    ).str.upper()

    # Find continent column

    continent_column = None

    for candidate in [
        "continent",
        "continent_code",
    ]:

        if candidate in countries.columns:

            continent_column = candidate
            break

    if continent_column is None:

        raise ValueError(
            "Could not find a continent column "
            "in countries.csv."
        )

    countries["continent"] = clean_text(
        countries[continent_column]
    ).str.upper()

    # --------------------------------------------------------
    # Merge airport → country
    # --------------------------------------------------------

    airport_reference = airports.merge(
        countries[
            [
                "code",
                "continent",
            ]
        ],
        left_on="iso_country",
        right_on="code",
        how="left",
    )

    airport_reference = airport_reference.drop(
        columns=["code"]
    )

    airport_reference["geographic_scope"] = (
        airport_reference.apply(
            lambda row: classify_scope(
                row["iso_country"],
                row["continent"],
            ),
            axis=1,
        )
    )

    # --------------------------------------------------------
    # Function to enrich one airport side
    # --------------------------------------------------------

    def enrich_side(df, airport_column, prefix):

        reference = airport_reference[
            [
                "ident",
                "name",
                "iata_code",
                "iso_country",
                "continent",
                "geographic_scope",
                "latitude_deg",
                "longitude_deg",
                "municipality",
            ]
        ].copy()

        reference = reference.rename(
            columns={
                "ident": airport_column,
                "name": f"{prefix}_airport_reference_name",
                "iata_code": f"{prefix}_airport_reference_iata",
                "iso_country": f"{prefix}_airport_country_code",
                "continent": f"{prefix}_airport_continent",
                "geographic_scope": f"{prefix}_airport_geographic_scope",
                "latitude_deg": f"{prefix}_airport_latitude",
                "longitude_deg": f"{prefix}_airport_longitude",
                "municipality": f"{prefix}_airport_municipality",
            }
        )

        reference[airport_column] = (
            reference[airport_column]
            .astype("string")
            .str.upper()
        )

        result = df.merge(
            reference,
            on=airport_column,
            how="left",
        )

        return result

    # --------------------------------------------------------
    # Enrich departure airport
    # --------------------------------------------------------

    print()
    print("[4/6] Enriching departure airports...")

    flights = enrich_side(
        flights,
        "departure_airport_icao",
        "departure",
    )

    # --------------------------------------------------------
    # Enrich arrival airport
    # --------------------------------------------------------

    print("Enriching arrival airports...")

    flights = enrich_side(
        flights,
        "arrival_airport_icao",
        "arrival",
    )

    # --------------------------------------------------------
    # Create final geography classification
    # --------------------------------------------------------

    print()
    print("[5/6] Creating geographic scope classification...")

    def network_scope(row):

        departure_scope = row[
            "departure_airport_geographic_scope"
        ]

        arrival_scope = row[
            "arrival_airport_geographic_scope"
        ]

        if pd.isna(departure_scope) or pd.isna(arrival_scope):
            return "Unknown"

        # Target network is Germany + Europe.
        # Since the transformed data already contains
        # at least one target German airport, this keeps
        # the geography classification explicit.

        if (
            departure_scope in ["Germany", "Europe"]
            and arrival_scope in ["Germany", "Europe"]
        ):
            return "Germany + Europe"

        if (
            departure_scope in ["Germany", "Europe"]
            or arrival_scope in ["Germany", "Europe"]
        ):
            return "Germany/Europe + Outside Europe"

        if (
            departure_scope == "Outside Europe"
            and arrival_scope == "Outside Europe"
        ):
            return "Outside Europe"

        return "Unknown"

    flights["network_geographic_scope"] = flights.apply(
        network_scope,
        axis=1,
    )

    # --------------------------------------------------------
    # Target airport IATA fallback
    # --------------------------------------------------------

    flights["departure_airport_iata"] = (
        flights["departure_airport_icao"]
        .map(TARGET_AIRPORTS)
        .fillna(
            flights["departure_airport_iata"]
        )
    )

    flights["arrival_airport_iata"] = (
        flights["arrival_airport_icao"]
        .map(TARGET_AIRPORTS)
        .fillna(
            flights["arrival_airport_iata"]
        )
    )

    # --------------------------------------------------------
    # Create country-level fields
    # --------------------------------------------------------

    flights["departure_country"] = (
        flights[
            "departure_airport_country_code"
        ]
        .fillna(
            flights["departure_country"]
        )
    )

    flights["arrival_country"] = (
        flights[
            "arrival_airport_country_code"
        ]
        .fillna(
            flights["arrival_country"]
        )
    )

    # --------------------------------------------------------
    # Create Europe flags
    # --------------------------------------------------------

    flights["departure_is_germany"] = (
        flights[
            "departure_airport_geographic_scope"
        ]
        == "Germany"
    )

    flights["arrival_is_germany"] = (
        flights[
            "arrival_airport_geographic_scope"
        ]
        == "Germany"
    )

    flights["departure_is_europe"] = (
        flights[
            "departure_airport_geographic_scope"
        ]
        .isin(["Germany", "Europe"])
    )

    flights["arrival_is_europe"] = (
        flights[
            "arrival_airport_geographic_scope"
        ]
        .isin(["Germany", "Europe"])
    )

    flights["both_endpoints_in_europe"] = (
        flights["departure_is_europe"]
        & flights["arrival_is_europe"]
    )

    # --------------------------------------------------------
    # Data quality status
    # --------------------------------------------------------

    flights["airport_reference_complete"] = (
        flights[
            "departure_airport_country_code"
        ].notna()
        &
        flights[
            "arrival_airport_country_code"
        ].notna()
    )

    # --------------------------------------------------------
    # Save enriched dataset
    # --------------------------------------------------------

    print()
    print("[6/6] Saving enriched dataset...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    flights.to_parquet(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Build quality report
    # --------------------------------------------------------

    report_rows = []

    total = len(flights)

    report_rows.append(
        {
            "metric": "total_records",
            "value": total,
            "percentage": 100.0,
        }
    )

    for column, label in [
        (
            "departure_airport_country_code",
            "known_departure_country",
        ),
        (
            "arrival_airport_country_code",
            "known_arrival_country",
        ),
        (
            "departure_airport_continent",
            "known_departure_continent",
        ),
        (
            "arrival_airport_continent",
            "known_arrival_continent",
        ),
        (
            "airport_reference_complete",
            "complete_airport_reference",
        ),
        (
            "both_endpoints_in_europe",
            "both_endpoints_in_europe",
        ),
    ]:

        if flights[column].dtype == bool:

            count = int(
                flights[column].sum()
            )

        else:

            count = int(
                flights[column].notna().sum()
            )

        percentage = (
            count / total * 100
            if total
            else 0
        )

        report_rows.append(
            {
                "metric": label,
                "value": count,
                "percentage": round(
                    percentage,
                    2,
                ),
            }
        )

    # Geographic scope counts

    scope_counts = (
        flights[
            "network_geographic_scope"
        ]
        .value_counts(dropna=False)
    )

    for scope, count in scope_counts.items():

        report_rows.append(
            {
                "metric": (
                    "network_scope_"
                    + str(scope)
                    .lower()
                    .replace(" ", "_")
                    .replace("+", "plus")
                    .replace("/", "_")
                ),
                "value": int(count),
                "percentage": round(
                    count / total * 100,
                    2,
                ),
            }
        )

    # Departure countries

    departure_countries = (
        flights[
            "departure_airport_country_code"
        ]
        .value_counts()
        .head(20)
    )

    for country, count in departure_countries.items():

        report_rows.append(
            {
                "metric": (
                    f"departure_country_{country}"
                ),
                "value": int(count),
                "percentage": round(
                    count / total * 100,
                    2,
                ),
            }
        )

    # Arrival countries

    arrival_countries = (
        flights[
            "arrival_airport_country_code"
        ]
        .value_counts()
        .head(20)
    )

    for country, count in arrival_countries.items():

        report_rows.append(
            {
                "metric": (
                    f"arrival_country_{country}"
                ),
                "value": int(count),
                "percentage": round(
                    count / total * 100,
                    2,
                ),
            }
        )

    report = pd.DataFrame(
        report_rows
    )

    report.to_csv(
        QUALITY_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Print final summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)

    print(
        f"Input records:              {total:,}"
    )

    known_departure = flights[
        "departure_airport_country_code"
    ].notna().sum()

    known_arrival = flights[
        "arrival_airport_country_code"
    ].notna().sum()

    complete_reference = flights[
        "airport_reference_complete"
    ].sum()

    europe_network = flights[
        "both_endpoints_in_europe"
    ].sum()

    print(
        f"Known departure country:     "
        f"{known_departure:,} "
        f"({known_departure / total * 100:.1f}%)"
    )

    print(
        f"Known arrival country:       "
        f"{known_arrival:,} "
        f"({known_arrival / total * 100:.1f}%)"
    )

    print(
        f"Complete airport reference:  "
        f"{complete_reference:,} "
        f"({complete_reference / total * 100:.1f}%)"
    )

    print(
        f"Both endpoints in Europe:    "
        f"{europe_network:,} "
        f"({europe_network / total * 100:.1f}%)"
    )

    print()
    print("Network geographic scope:")
    print(
        flights[
            "network_geographic_scope"
        ]
        .value_counts(dropna=False)
        .to_string()
    )

    print()
    print("Top departure countries:")
    print(
        flights[
            "departure_airport_country_code"
        ]
        .value_counts()
        .head(15)
        .to_string()
    )

    print()
    print("Top arrival countries:")
    print(
        flights[
            "arrival_airport_country_code"
        ]
        .value_counts()
        .head(15)
        .to_string()
    )

    print()
    print("Output:")
    print(OUTPUT_FILE)

    print()
    print("Quality report:")
    print(QUALITY_FILE)

    print()
    print("DONE")


if __name__ == "__main__":
    main()