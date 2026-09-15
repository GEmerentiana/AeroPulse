-- AeroPulse
-- Production route-airline price aggregation
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_route_airline_price_production`
AS

SELECT
  route_identifier,
  origin_iata,
  destination_iata,
  departure_date,
  airline_name,
  airline_iata,

  COUNT(*) AS price_observations,

  MIN(price_eur) AS minimum_price_eur,

  AVG(price_eur) AS average_price_eur,

  MAX(price_eur) AS maximum_price_eur,

  CASE
    WHEN COUNT(*) >= 10 THEN 'Strong Sample'
    WHEN COUNT(*) >= 3 THEN 'Moderate Sample'
    ELSE 'Limited Sample'
  END AS price_sample_quality

FROM
  `aeropulse-aviation.aviation_performance.fact_route_price_observations_production`

WHERE
  currency = 'EUR'
  AND cabin_class = 'economy'

GROUP BY
  route_identifier,
  origin_iata,
  destination_iata,
  departure_date,
  airline_name,
  airline_iata;