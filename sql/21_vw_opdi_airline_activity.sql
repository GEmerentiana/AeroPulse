CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_opdi_airline_activity`
AS
SELECT
  route_identifier,
  icao_operator,

  COUNT(*) AS observed_flights,

  COUNTIF(observed_start_period = 'Morning') AS morning_flights,

  COUNTIF(observed_start_period = 'Afternoon') AS afternoon_flights,

  COUNTIF(observed_start_period = 'Evening') AS evening_flights,

  COUNTIF(observed_start_period = 'Night') AS night_flights

FROM
  `aeropulse-aviation.aviation_performance.fact_opdi_flights`

WHERE
  icao_operator IS NOT NULL

GROUP BY
  route_identifier,
  icao_operator;