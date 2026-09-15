-- AeroPulse
-- Advisor recommendation ranking and explanation
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_recommendation_v2`
AS

SELECT
  f.route_identifier,
  f.airline_name,
  f.month,
  f.preferred_time,
  f.monthly_service_score,
  f.time_fit_score,
  f.advisor_route_airline_score,
  f.average_price_eur,
  f.price_observations,
  f.price_sample_quality,
  f.reliable_price_score,

  COALESCE(
    e.price_evidence_status,
    'No Price Data'
  ) AS price_evidence_status,

  f.advisor_score,

  ROW_NUMBER() OVER (
    PARTITION BY
      f.route_identifier,
      f.month,
      f.preferred_time
    ORDER BY
      f.advisor_score DESC,
      f.monthly_service_score DESC,
      f.time_fit_score DESC,
      f.advisor_route_airline_score DESC,
      f.reliable_price_score DESC,
      f.airline_name ASC
  ) AS advisor_rank,

  CASE
    WHEN f.advisor_score >= 80 THEN 'Excellent Choice'
    WHEN f.advisor_score >= 70 THEN 'Strong Choice'
    WHEN f.advisor_score >= 60 THEN 'Good Choice'
    WHEN f.advisor_score >= 50 THEN 'Consider'
    ELSE 'Lower Priority'
  END AS recommendation_level,

  CASE
    WHEN e.price_evidence_status IS NULL THEN
      'Recommended based on service activity, preferred-time fit and route-airline performance; no price observation is available.'

    WHEN e.price_evidence_status = 'Limited Price Evidence' THEN
      'Recommended based on service activity, preferred-time fit, route-airline performance and limited price evidence.'

    ELSE
      'Recommended based on service activity, preferred-time fit, route-airline performance and available price evidence.'
  END AS recommendation_reason

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_final_score_v3` f

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_evidence` e
ON
  f.route_identifier = e.route_identifier
  AND f.airline_name = e.airline_name;