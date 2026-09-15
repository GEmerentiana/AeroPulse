-- AeroPulse
-- Selects the user's preferred time period and applies the corresponding
-- time-fit score and observed activity share.
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_selected_time`
AS

SELECT
  t.route_identifier,
  t.airline_name,
  t.month,
  t.observed_flights,

  p.preferred_time,

  CASE
    WHEN p.preferred_time = 'Morning'
      THEN t.morning_time_fit_score

    WHEN p.preferred_time = 'Afternoon'
      THEN t.afternoon_time_fit_score

    WHEN p.preferred_time = 'Evening'
      THEN t.evening_time_fit_score

    WHEN p.preferred_time = 'Night'
      THEN t.night_time_fit_score
  END AS time_fit_score,

  CASE
    WHEN p.preferred_time = 'Morning'
      THEN t.morning_activity_pct

    WHEN p.preferred_time = 'Afternoon'
      THEN t.afternoon_activity_pct

    WHEN p.preferred_time = 'Evening'
      THEN t.evening_activity_pct

    WHEN p.preferred_time = 'Night'
      THEN t.night_activity_pct
  END AS selected_time_activity_pct

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_time_fit` AS t

CROSS JOIN
  `aeropulse-aviation.aviation_performance.vw_aeropulse_time_periods` AS p;