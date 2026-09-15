-- AeroPulse
-- Route × airline × month observed activity aggregation
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_airline_month`
AS

SELECT
  r.adep,
  r.ades,
  CONCAT(r.adep, '-', r.ades) AS route_identifier,
  r.month,
  r.icao_operator,
  m.airline_name,

  r.observed_flights,
  r.morning_flights,
  r.afternoon_flights,
  r.evening_flights,
  r.night_flights,

  ROUND(
    SAFE_DIVIDE(
      r.observed_flights,
      SUM(r.observed_flights) OVER (
        PARTITION BY r.adep, r.ades, r.month
      )
    ) * 100,
    2
  ) AS monthly_activity_share_pct,

  ROUND(
    SAFE_DIVIDE(
      r.morning_flights,
      r.observed_flights
    ) * 100,
    2
  ) AS morning_activity_pct,

  ROUND(
    SAFE_DIVIDE(
      r.afternoon_flights,
      r.observed_flights
    ) * 100,
    2
  ) AS afternoon_activity_pct,

  ROUND(
    SAFE_DIVIDE(
      r.evening_flights,
      r.observed_flights
    ) * 100,
    2
  ) AS evening_activity_pct,

  ROUND(
    SAFE_DIVIDE(
      r.night_flights,
      r.observed_flights
    ) * 100,
    2
  ) AS night_activity_pct

FROM
  `aeropulse-aviation.aviation_performance.fact_aeropulse_advisor_airline_month` AS r

INNER JOIN
  `aeropulse-aviation.aviation_performance.aeropulse_operator_airline_reference` AS m
ON
  r.icao_operator = m.icao_operator;