-- AeroPulse
-- Monthly observed flight activity strength scoring
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_activity_strength`
AS

SELECT
  route_identifier,
  airline_name,
  month,
  observed_flights,

  CASE
    WHEN observed_flights <= 4 THEN 'Limited'
    WHEN observed_flights <= 17 THEN 'Moderate'
    WHEN observed_flights <= 48 THEN 'Strong'
    ELSE 'Very Strong'
  END AS activity_strength,

  CASE
    WHEN observed_flights <= 4 THEN 20
    WHEN observed_flights <= 17 THEN 40
    WHEN observed_flights <= 48 THEN 70
    ELSE 100
  END AS activity_strength_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_month`;