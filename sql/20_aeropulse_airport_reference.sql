-- AeroPulse
-- Airport reference table
-- BigQuery dataset: aviation_performance
--
-- Derived airport reference used to enrich route records with
-- IATA codes, airport names, cities and country information.
--
-- Production table contains 1,103 airport records.
-- The repository stores the table definition rather than the
-- production reference data.

CREATE TABLE IF NOT EXISTS
`aeropulse-aviation.aviation_performance.aeropulse_airport_reference`
(
  airport_icao STRING,
  airport_iata STRING,
  airport_name STRING,
  airport_city STRING,
  country_code STRING,
  match_status STRING,
  country_name STRING
);