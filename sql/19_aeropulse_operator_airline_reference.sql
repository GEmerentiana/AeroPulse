-- AeroPulse
-- ICAO operator → AeroPulse airline reference
-- BigQuery dataset: aviation_performance
--
-- 28 mapped airlines.
-- The production table contains the mapping values; this repository
-- stores the table definition separately from the production data.

CREATE TABLE IF NOT EXISTS
`aeropulse-aviation.aviation_performance.aeropulse_operator_airline_reference`
(
  icao_operator STRING,
  airline_name STRING
);