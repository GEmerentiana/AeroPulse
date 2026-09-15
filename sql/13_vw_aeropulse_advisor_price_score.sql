-- AeroPulse
-- Route-relative price competitiveness scoring
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_score`
AS

SELECT
  route_identifier,
  airline_name,
  average_price_eur,
  price_observations,
  price_sample_quality,

  ROUND(
    SAFE_DIVIDE(
      MIN(average_price_eur) OVER (
        PARTITION BY route_identifier
      ),
      average_price_eur
    ) * 100,
    2
  ) AS route_price_competitiveness_score

FROM
  `aeropulse-aviation.aviation_performance.vw_route_airline_price_production`

WHERE
  average_price_eur IS NOT NULL;