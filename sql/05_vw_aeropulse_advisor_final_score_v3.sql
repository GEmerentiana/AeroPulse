-- AeroPulse
-- Final Flight Choice Advisor scoring model
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_final_score_v3`
AS

SELECT
  s.route_identifier,
  s.airline_name,
  s.month,
  s.preferred_time,

  m.monthly_service_score,
  s.time_fit_score,

  r.advisor_route_airline_score,

  ps.average_price_eur,
  ps.price_observations,
  ps.price_sample_quality,
  ps.reliable_price_score,

  ROUND(
    SAFE_DIVIDE(
      (m.monthly_service_score * 0.35)
      + (s.time_fit_score * 0.25)
      + (r.advisor_route_airline_score * 0.25)
      + (COALESCE(ps.reliable_price_score, 0) * 0.15),

      CASE
        WHEN ps.reliable_price_score IS NOT NULL
          THEN 1.00
        ELSE
          0.85
      END
    ),
    2
  ) AS advisor_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_selected_time` s

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_monthly_service` m

ON
  s.route_identifier = m.route_identifier
  AND s.airline_name = m.airline_name
  AND s.month = m.month

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_airline_score` r

ON
  s.route_identifier = r.route_identifier
  AND s.airline_name = r.airline_name

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_price_reliability` ps

ON
  s.route_identifier = ps.route_identifier
  AND s.airline_name = ps.airline_name;