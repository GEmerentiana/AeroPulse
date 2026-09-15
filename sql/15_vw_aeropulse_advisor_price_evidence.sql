-- AeroPulse
-- Price evidence status classification
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_evidence`
AS

SELECT
  route_identifier,
  airline_name,
  average_price_eur,
  price_observations,
  price_sample_quality,
  route_price_competitiveness_score,
  price_reliability_factor,
  reliable_price_score,

  CASE
    WHEN price_observations >= 10
      THEN 'Strong Price Evidence'

    WHEN price_observations >= 3
      THEN 'Moderate Price Evidence'

    WHEN price_observations >= 1
      THEN 'Limited Price Evidence'

    ELSE 'No Price Data'
  END AS price_evidence_status

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_reliability`;