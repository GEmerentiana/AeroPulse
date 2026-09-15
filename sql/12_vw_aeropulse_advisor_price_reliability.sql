-- AeroPulse
-- Price evidence reliability adjustment
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_reliability`
AS

SELECT
  route_identifier,
  airline_name,
  average_price_eur,
  price_observations,
  price_sample_quality,
  route_price_competitiveness_score,

  CASE
    WHEN price_sample_quality = 'Strong Sample'
      THEN 1.00

    WHEN price_sample_quality = 'Moderate Sample'
      THEN 0.85

    WHEN price_sample_quality = 'Limited Sample'
      THEN 0.60

    ELSE 0.00
  END AS price_reliability_factor,

  ROUND(
    route_price_competitiveness_score *
    CASE
      WHEN price_sample_quality = 'Strong Sample'
        THEN 1.00

      WHEN price_sample_quality = 'Moderate Sample'
        THEN 0.85

      WHEN price_sample_quality = 'Limited Sample'
        THEN 0.60

      ELSE 0.00
    END,
    2
  ) AS reliable_price_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_score`;