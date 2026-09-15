# AeroPulse — Initial Data Model

## Flight Fact

The central fact table will represent flight observations.

Potential fields:

* flight_date
* airline
* flight_number
* origin_airport
* destination_airport
* scheduled_departure
* scheduled_arrival
* actual_departure
* actual_arrival
* departure_delay_minutes
* arrival_delay_minutes
* cancellation_flag
* cancellation_reason

## Airline Dimension

Fields:

* airline_key
* airline_name
* iata_code
* icao_code
* airline_type

## Airport Dimension

Fields:

* airport_key
* airport_name
* iata_code
* icao_code
* city
* country

## Date Dimension

Fields:

* date_key
* date
* year
* month
* month_name
* day
* day_of_week
* season
* is_weekend
* is_public_holiday
* holiday_name

## Route Dimension

Fields:

* route_key
* origin_airport
* destination_airport
* destination_city
* destination_country
* route_type

## Price Data

If ticket prices come from a separate source, price data will initially be treated as a separate dataset.

Potential fields:

* price_date
* origin
* destination
* airline
* ticket_price
* currency
* cabin_class
* source

## Data Integration

The preferred join keys are:

* date
* origin
* destination
* airline

If exact flight-level price matching is not possible, price analysis will be performed at an appropriate aggregated level such as:

* route + date
* route + airline + date
* route + month
* route + airline + month

The final granularity will depend on the selected price source.

## Data Quality Requirements

The pipeline must check:

* missing dates
* invalid airport codes
* invalid airline codes
* duplicate flights
* negative delays
* invalid prices
* invalid currencies
* impossible dates
* cancellation inconsistencies
* missing origin/destination
