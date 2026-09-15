-- AeroPulse
-- Monthly route × operator activity fact table
-- BigQuery dataset: aviation_performance
--
-- Source: derived from AeroPulse OPDI flight observations.
-- This repository stores the table definition, not the production data rows.

CREATE TABLE IF NOT EXISTS
`aeropulse-aviation.aviation_performance.fact_aeropulse_advisor_airline_month`
(
  adep STRING,
  ades STRING,
  month STRING,
  icao_operator STRING,
  observed_flights INT64,
  morning_flights INT64,
  afternoon_flights INT64,
  evening_flights INT64,
  night_flights INT64
);