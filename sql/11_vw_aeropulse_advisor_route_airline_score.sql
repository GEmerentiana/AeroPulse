-- AeroPulse
-- Route-airline performance and consistency score
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_airline_score`
AS

SELECT
  m.route_identifier,
  m.airline_name,

  c.active_months,
  c.consistency_level,
  c.service_consistency_score,

  ROUND(
    AVG(m.activity_strength_score),
    2
  ) AS average_activity_strength_score,

  ROUND(
    (c.service_consistency_score * 0.40)
    +
    (AVG(m.activity_strength_score) * 0.60),
    2
  ) AS advisor_route_airline_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_monthly_service` m

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_consistency` c

ON
  m.route_identifier = c.route_identifier
  AND m.airline_name = c.airline_name

GROUP BY
  m.route_identifier,
  m.airline_name,
  c.active_months,
  c.consistency_level,
  c.service_consistency_score;