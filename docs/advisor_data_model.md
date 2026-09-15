# AeroPulse Flight Choice Advisor — Data Model

## Advisor activity fact

The Flight Choice Advisor uses the BigQuery table:

`aeropulse-aviation.aviation_performance.fact_aeropulse_advisor_airline_month`

This is a physical aggregate table at the following grain:

**route × month × ICAO operator**

### Fields

| Field | Type | Description |
|---|---|---|
| `adep` | STRING | Departure airport ICAO code |
| `ades` | STRING | Arrival airport ICAO code |
| `month` | STRING | Observation month (`YYYY-MM`) |
| `icao_operator` | STRING | ICAO operator code |
| `observed_flights` | INT64 | Number of observed flights |
| `morning_flights` | INT64 | Observed flights in the Morning period |
| `afternoon_flights` | INT64 | Observed flights in the Afternoon period |
| `evening_flights` | INT64 | Observed flights in the Evening period |
| `night_flights` | INT64 | Observed flights in the Night period |

## Current production coverage

- Observation period: August 2025 – July 2026
- Rows: 11,842
- Unique route-month combinations: 2,838
- Total observed flights represented: 269,452

## Upstream relationship

The advisor activity logic is derived from OPDI flight observations.

The repository contains the following reusable aggregation view:

`vw_opdi_airline_activity`

This view aggregates `fact_opdi_flights` by route and ICAO operator and calculates total observed flights plus the four broad observed activity periods:

- Morning
- Afternoon
- Evening
- Night

The monthly advisor fact table additionally contains the `month` dimension.

## Provenance note

The historical 12-month population of `fact_aeropulse_advisor_airline_month` was created during the earlier AeroPulse OPDI data-preparation workflow.

The original population/transformation script is not currently preserved in the repository. The table is therefore documented as a derived production aggregate rather than presenting a reconstructed transformation as if it were the original implementation.

The current `fact_opdi_flights` table should not be treated as a reproducible source for the historical 12-month table because it currently contains only the July 2026 OPDI slice.

## Downstream usage

The table feeds:

`vw_aeropulse_advisor_airline_month`

which adds airline mapping and calculates:

- monthly activity share
- Morning activity percentage
- Afternoon activity percentage
- Evening activity percentage
- Night activity percentage

These outputs feed the Flight Choice Advisor scoring layer.