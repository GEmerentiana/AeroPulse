-- AeroPulse
-- Final Flight Choice Advisor dashboard view
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_flight_choice_dashboard`
AS

SELECT
  r.route_identifier,
  r.origin_iata,
  r.destination_iata,

  r.origin_city,
  r.destination_city,

  r.origin_country,
  r.destination_country,

  -- User-friendly airport selectors
  CONCAT(
    r.origin_iata,
    ' — ',
    r.origin_city,
    ' — ',
    r.origin_country
  ) AS origin_display,

  CONCAT(
    r.destination_iata,
    ' — ',
    r.destination_city,
    ' — ',
    r.destination_country
  ) AS destination_display,

  r.route_type,
  r.route_display,

  -- Historical month used internally by the recommendation model
  f.month,

  -- Future-facing month shown to the dashboard user
  FORMAT_DATE(
    '%B',
    PARSE_DATE('%Y-%m', f.month)
  ) AS travel_month,

  f.preferred_time,
  f.airline_name,
  f.advisor_score,
  f.recommendation_level,
  f.recommendation_reason,
  f.monthly_service_score,
  f.time_fit_score,
  f.advisor_route_airline_score,
  f.average_price_eur,
  f.price_observations,
  f.price_sample_quality,
  f.reliable_price_score,
  f.price_evidence_status

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_recommendation_v2` f

LEFT JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_month` r
ON
  f.route_identifier = r.route_identifier
  AND f.airline_name = r.airline_name
  AND f.month = r.month

WHERE
  f.advisor_rank = 1;