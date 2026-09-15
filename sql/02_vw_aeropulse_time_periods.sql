-- AeroPulse
-- User-selectable broad time periods for the Flight Choice Advisor
-- BigQuery dataset: aviation_performance

CREATE OR REPLACE VIEW
`aeropulse-aviation.aviation_performance.vw_aeropulse_time_periods`
AS

SELECT 'Morning' AS preferred_time
UNION ALL
SELECT 'Afternoon'
UNION ALL
SELECT 'Evening'
UNION ALL
SELECT 'Night';