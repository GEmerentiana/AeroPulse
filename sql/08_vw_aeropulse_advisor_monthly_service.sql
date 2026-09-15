-- AeroPulse
-- Monthly airline service activity score
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_monthly_service`
AS

SELECT
  a.route_identifier,
  a.airline_name,
  a.month,
  a.observed_flights,
  a.activity_strength,
  a.activity_strength_score,

  c.active_months,
  c.consistency_level,
  c.service_consistency_score,

  ROUND(
    (a.activity_strength_score * 0.60)
    + (c.service_consistency_score * 0.40),
    2
  ) AS monthly_service_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_activity_strength` AS a

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_consistency` AS c

ON
  a.route_identifier = c.route_identifier
  AND a.airline_name = c.airline_name;