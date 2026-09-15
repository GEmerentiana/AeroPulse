import os
import csv
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv


# ============================================================
# 1. LOAD DUFFEL ACCESS TOKEN
# ============================================================

load_dotenv()

token = os.getenv("DUFFEL_ACCESS_TOKEN")

if not token:
    raise ValueError(
        "DUFFEL_ACCESS_TOKEN was not found in the .env file."
    )


# ============================================================
# 2. FILE PATHS
# ============================================================

routes_file = "data/duffel_routes.csv"
output_file = "data/route_price_observations.csv"


# ============================================================
# 3. DUFFEL API SETTINGS
# ============================================================

url = "https://api.duffel.com/air/offer_requests"

headers = {
    "Authorization": f"Bearer {token}",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ============================================================
# 4. STANDARD SEARCH SETTINGS
# ============================================================

departure_date = "2026-10-15"

cabin_class = "economy"

passenger = {
    "type": "adult"
}


# ============================================================
# 5. LOAD ROUTES
# ============================================================

routes = []

with open(
    routes_file,
    "r",
    encoding="utf-8"
) as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:
        routes.append(row)


print()
print("============================================================")
print("AEROPULSE DUFFEL PRICE COLLECTOR")
print("============================================================")
print()
print(f"Routes loaded: {len(routes)}")
print(f"Departure date: {departure_date}")
print(f"Cabin class: {cabin_class}")
print()


# ============================================================
# 6. CREATE PRICE OBSERVATION LIST
# ============================================================

new_rows = []

search_date = datetime.now(
    timezone.utc
).date().isoformat()


# ============================================================
# 7. SEARCH EACH ROUTE
# ============================================================

for index, route in enumerate(routes, start=1):

    route_identifier = route["route_identifier"]
    origin = route["origin_iata"]
    destination = route["destination_iata"]

    print(
        f"[{index}/{len(routes)}] "
        f"Searching {route_identifier} "
        f"({origin} -> {destination})..."
    )

    payload = {
        "data": {
            "slices": [
                {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date
                }
            ],
            "passengers": [
                passenger
            ],
            "cabin_class": cabin_class
        }
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

    except requests.RequestException as error:

        print(
            f"   ERROR: API request failed: {error}"
        )

        continue


    # ========================================================
    # 8. CHECK API RESPONSE
    # ========================================================

    if response.status_code != 201:

        print(
            f"   ERROR: HTTP {response.status_code}"
        )

        print(
            f"   {response.text}"
        )

        continue


    # ========================================================
    # 9. READ OFFERS
    # ========================================================

    try:

        data = response.json()["data"]

    except (KeyError, ValueError):

        print(
            "   ERROR: Could not read API response."
        )

        continue


    offers = data.get(
        "offers",
        []
    )

    print(
        f"   Offers returned: {len(offers)}"
    )


    route_observations = 0


    # ========================================================
    # 10. PROCESS EACH OFFER
    # ========================================================

    for offer in offers:

        # ----------------------------------------------------
        # IMPORTANT:
        # Store Duffel's unique offer ID.
        # ----------------------------------------------------

        offer_id = offer.get(
            "id"
        )

        if not offer_id:
            continue


        total_price = offer.get(
            "total_amount"
        )

        currency = offer.get(
            "total_currency"
        )

        slices = offer.get(
            "slices",
            []
        )

        if not slices:
            continue


        segments = slices[0].get(
            "segments",
            []
        )

        if not segments:
            continue


        segment = segments[0]


        # ====================================================
        # 11. GET AIRLINE INFORMATION
        # ====================================================

        airline = segment.get(
            "marketing_carrier",
            {}
        )

        airline_name = airline.get(
            "name"
        )

        airline_iata = airline.get(
            "iata_code"
        )


        # ====================================================
        # 12. EXCLUDE DUFFEL TEST AIRLINE
        # ====================================================

        if airline_iata == "ZZ":

            continue


        # ====================================================
        # 13. GET FLIGHT TIMES
        # ====================================================

        departure_time = segment.get(
            "departing_at"
        )

        arrival_time = segment.get(
            "arriving_at"
        )


        # ====================================================
        # 14. STORE OBSERVATION
        # ====================================================

        new_rows.append(
            {
                "offer_id": offer_id,
                "search_date": search_date,
                "departure_date": departure_date,
                "origin_iata": origin,
                "destination_iata": destination,
                "route_identifier": route_identifier,
                "airline_name": airline_name,
                "airline_iata": airline_iata,
                "price_eur": total_price,
                "currency": currency,
                "cabin_class": cabin_class,
                "departure_time": departure_time,
                "arrival_time": arrival_time
            }
        )

        route_observations += 1


    print(
        f"   Valid observations added: "
        f"{route_observations}"
    )

    print()


# ============================================================
# 15. DEFINE CSV COLUMNS
# ============================================================

fieldnames = [
    "offer_id",
    "search_date",
    "departure_date",
    "origin_iata",
    "destination_iata",
    "route_identifier",
    "airline_name",
    "airline_iata",
    "price_eur",
    "currency",
    "cabin_class",
    "departure_time",
    "arrival_time"
]


# ============================================================
# 16. HANDLE EXISTING CSV
# ============================================================

file_exists = os.path.exists(
    output_file
)


# ============================================================
# 17. APPEND NEW OBSERVATIONS
# ============================================================

with open(
    output_file,
    "a",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    # Write the new header if the file doesn't exist
    # or is empty.
    if not file_exists or os.path.getsize(output_file) == 0:

        writer.writeheader()

    writer.writerows(new_rows)


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print("============================================================")
print("COLLECTION COMPLETE")
print("============================================================")
print()
print(
    f"Routes searched: {len(routes)}"
)
print(
    f"New price observations: {len(new_rows)}"
)
print(
    f"Search date: {search_date}"
)
print(
    f"Departure date: {departure_date}"
)
print(
    f"Saved to: {output_file}"
)
print()