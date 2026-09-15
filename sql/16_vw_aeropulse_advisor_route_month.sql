-- AeroPulse
-- Route × airline × month foundation for the Flight Choice Advisor
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_route_month`
AS

SELECT
  a.route_identifier,
  a.adep,
  a.ades,

  o.airport_iata AS origin_iata,
  o.airport_name AS origin_airport_name,
  o.airport_city AS origin_city,
  o.country_code AS origin_country_code,
  o.country_name AS origin_country,

  d.airport_iata AS destination_iata,
  d.airport_name AS destination_airport_name,
  d.airport_city AS destination_city,
  d.country_code AS destination_country_code,
  d.country_name AS destination_country,

  CASE
    WHEN o.country_code = 'DE'
      AND d.country_code = 'DE'
      THEN 'Domestic'

    WHEN o.country_code = 'DE'
      AND d.country_code IS NOT NULL
      AND d.country_code != 'DE'
      THEN 'International'

    ELSE 'Unknown'
  END AS route_type,

  CONCAT(
    o.airport_city,
    ' → ',
    d.airport_city
  ) AS route_display,

  a.month,
  a.icao_operator,
  a.airline_name,

  a.observed_flights,
  a.morning_flights,
  a.afternoon_flights,
  a.evening_flights,
  a.night_flights,

  a.monthly_activity_share_pct,

  a.morning_activity_pct,
  a.afternoon_activity_pct,
  a.evening_activity_pct,
  a.night_activity_pct

FROM
  `aeropulse-aviation.aviation_performance.vw_aeropulse_advisor_airline_month` AS a

LEFT JOIN
  `aeropulse-aviation.aviation_performance.aeropulse_airport_reference` AS o
ON
  a.adep = o.airport_icao

LEFT JOIN
  `aeropulse-aviation.aviation_performance.aeropulse_airport_reference` AS d
ON
  a.ades = d.airport_icao;