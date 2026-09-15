# AeroPulse — Analytical Variables

## Date Variables

- date
- year
- month
- day
- day_of_week
- season
- is_weekend

## Holiday Variables

- is_public_holiday
- holiday_name
- holiday_type
- is_pre_holiday
- is_post_holiday

## Airport Variables

- origin_airport
- destination_airport
- destination_city
- destination_country

## Route Variables

- route
- route_type

Route types:

- Domestic
- International

## Airline Variables

- airline
- airline_iata
- airline_icao
- airline_type

Airline types:
- Legacy
- Low Cost

## Flight Variables

- flight_number
- scheduled_departure
- scheduled_arrival
- actual_departure
- actual_arrival
- flight_time
- flight_count

## Price Variables

- ticket_price
- average_ticket_price
- median_ticket_price

## Delay Variables

- departure_delay_minutes
- arrival_delay_minutes
- average_delay_minutes
- delay_flag
- delay_rate

## Cancellation Variables

- cancellation_flag
- cancellation_rate
- cancellation_reason

Cancellation reason will only be used if available.

## Derived Variables

- route_growth
- airline_growth
- route_strength
- demand_score
- price_score
- punctuality_score
- reliability_score
- seasonality_score
- recommendation_score

## Data Freshness Variables
- data_available_through
- pipeline_refresh_date
- pipeline_refresh_timestamp
- analysis_start_date
- analysis_end_date