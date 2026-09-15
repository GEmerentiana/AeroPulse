-- ============================================================
-- AeroPulse
-- Fact Tables
-- ============================================================

CREATE TABLE IF NOT EXISTS
  `${GCP_PROJECT_ID}.aviation_performance.fact_flights`
(
  flight_id STRING NOT NULL,
  flight_date DATE NOT NULL,

  airline_iata STRING,
  flight_number STRING,

  origin_iata STRING,
  destination_iata STRING,

  scheduled_departure TIMESTAMP,
  actual_departure TIMESTAMP,

  scheduled_arrival TIMESTAMP,
  actual_arrival TIMESTAMP,

  departure_delay_minutes INT64,
  arrival_delay_minutes INT64,

  cancelled BOOL,
  cancellation_reason STRING,

  aircraft_icao24 STRING,

  source STRING NOT NULL,
  source_record_id STRING,

  loaded_at TIMESTAMP NOT NULL
)
PARTITION BY flight_date
CLUSTER BY origin_iata, destination_iata, airline_iata
OPTIONS (
  description = 'AeroPulse flight-level observations'
);


-- ============================================================
-- FACT AIRFARES
-- ============================================================

CREATE TABLE IF NOT EXISTS
  `${GCP_PROJECT_ID}.aviation_performance.fact_airfares`
(
  fare_id STRING NOT NULL,
  observation_date DATE NOT NULL,

  airline_iata STRING,
  origin_iata STRING,
  destination_iata STRING,

  price NUMERIC,
  currency STRING,

  cabin_class STRING,
  stops INT64,
  advance_purchase_days INT64,

  travel_date DATE,

  source STRING NOT NULL,
  source_record_id STRING,

  loaded_at TIMESTAMP NOT NULL
)
PARTITION BY observation_date
CLUSTER BY origin_iata, destination_iata, airline_iata
OPTIONS (
  description = 'AeroPulse fare observations'
);