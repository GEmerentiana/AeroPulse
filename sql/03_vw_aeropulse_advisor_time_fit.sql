-- AeroPulse
-- Time-of-day activity strength and fit scoring
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_time_fit`
AS

SELECT
  m.route_identifier,
  m.airline_name,
  m.month,
  m.observed_flights,

  m.morning_activity_pct,
  m.afternoon_activity_pct,
  m.evening_activity_pct,
  m.night_activity_pct,

  CASE
    WHEN m.morning_activity_pct >= 50 THEN 'Very Strong'
    WHEN m.morning_activity_pct >= 35 THEN 'Strong'
    WHEN m.morning_activity_pct >= 20 THEN 'Moderate'
    WHEN m.morning_activity_pct >= 10 THEN 'Limited'
    ELSE 'Very Limited'
  END AS morning_time_strength,

  CASE
    WHEN m.afternoon_activity_pct >= 50 THEN 'Very Strong'
    WHEN m.afternoon_activity_pct >= 35 THEN 'Strong'
    WHEN m.afternoon_activity_pct >= 20 THEN 'Moderate'
    WHEN m.afternoon_activity_pct >= 10 THEN 'Limited'
    ELSE 'Very Limited'
  END AS afternoon_time_strength,

  CASE
    WHEN m.evening_activity_pct >= 50 THEN 'Very Strong'
    WHEN m.evening_activity_pct >= 35 THEN 'Strong'
    WHEN m.evening_activity_pct >= 20 THEN 'Moderate'
    WHEN m.evening_activity_pct >= 10 THEN 'Limited'
    ELSE 'Very Limited'
  END AS evening_time_strength,

  CASE
    WHEN m.night_activity_pct >= 50 THEN 'Very Strong'
    WHEN m.night_activity_pct >= 35 THEN 'Strong'
    WHEN m.night_activity_pct >= 20 THEN 'Moderate'
    WHEN m.night_activity_pct >= 10 THEN 'Limited'
    ELSE 'Very Limited'
  END AS night_time_strength,

  CASE
    WHEN m.morning_activity_pct >= 50 THEN 100
    WHEN m.morning_activity_pct >= 35 THEN 80
    WHEN m.morning_activity_pct >= 20 THEN 60
    WHEN m.morning_activity_pct >= 10 THEN 40
    ELSE 20
  END AS morning_time_fit_score,

  CASE
    WHEN m.afternoon_activity_pct >= 50 THEN 100
    WHEN m.afternoon_activity_pct >= 35 THEN 80
    WHEN m.afternoon_activity_pct >= 20 THEN 60
    WHEN m.afternoon_activity_pct >= 10 THEN 40
    ELSE 20
  END AS afternoon_time_fit_score,

  CASE
    WHEN m.evening_activity_pct >= 50 THEN 100
    WHEN m.evening_activity_pct >= 35 THEN 80
    WHEN m.evening_activity_pct >= 20 THEN 60
    WHEN m.evening_activity_pct >= 10 THEN 40
    ELSE 20
  END AS evening_time_fit_score,

  CASE
    WHEN m.night_activity_pct >= 50 THEN 100
    WHEN m.night_activity_pct >= 35 THEN 80
    WHEN m.night_activity_pct >= 20 THEN 60
    WHEN m.night_activity_pct >= 10 THEN 40
    ELSE 20
  END AS night_time_fit_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_month` AS m;