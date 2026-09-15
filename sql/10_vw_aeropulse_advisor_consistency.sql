-- AeroPulse
-- Route-airline service consistency scoring
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_consistency`
AS

SELECT
  route_identifier,
  airline_name,

  COUNT(DISTINCT month) AS active_months,

  CASE
    WHEN COUNT(DISTINCT month) <= 2 THEN 'Very Limited'
    WHEN COUNT(DISTINCT month) <= 5 THEN 'Seasonal'
    WHEN COUNT(DISTINCT month) <= 8 THEN 'Established'
    WHEN COUNT(DISTINCT month) <= 11 THEN 'Highly Consistent'
    WHEN COUNT(DISTINCT month) = 12 THEN 'Year-Round'
  END AS consistency_level,

  CASE
    WHEN COUNT(DISTINCT month) <= 2 THEN 20
    WHEN COUNT(DISTINCT month) <= 5 THEN 40
    WHEN COUNT(DISTINCT month) <= 8 THEN 60
    WHEN COUNT(DISTINCT month) <= 11 THEN 80
    WHEN COUNT(DISTINCT month) = 12 THEN 100
  END AS service_consistency_score

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_month`

GROUP BY
  route_identifier,
  airline_name;