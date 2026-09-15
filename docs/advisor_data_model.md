# AeroPulse Flight Choice Advisor — Data Model

## Overview

The Flight Choice Advisor is built on a historical OPDI flight-observation dataset covering August 2025 through July 2026.

The advisor evaluates route and airline activity by month and observed activity period, then combines these signals with service consistency, route-airline strength, and price evidence to produce airline recommendations.

## Advisor activity fact

The core activity input is the BigQuery table:

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

## Production coverage

The current production aggregate represents:

- Observation period: August 2025 – July 2026
- Rows: 11,842
- Unique route-month combinations: 2,838
- Total observed flights represented: 269,452

The aggregate covers the route and operator population used by the production Flight Choice Advisor.

## Upstream data

The underlying aviation observations come from the OpenSky Network's Open Data for Performance and Infrastructure (OPDI).

The repository contains the historical OPDI preparation pipeline used to:

1. process the monthly OPDI flight files;
2. standardize flight-level fields;
3. enrich airport information using OurAirports;
4. validate the resulting historical dataset; and
5. load the processed data into BigQuery staging.

The repository also contains the reusable view:

`vw_opdi_airline_activity`

This view aggregates OPDI flight observations by route and ICAO operator and calculates:

- observed flights
- Morning activity
- Afternoon activity
- Evening activity
- Night activity

The production advisor fact adds the monthly dimension required for month-specific recommendations.

## Observed activity periods

The Advisor uses four broad observed activity periods:

- Morning
- Afternoon
- Evening
- Night

These periods describe when flight activity was observed in the OPDI data. They should not be interpreted as scheduled commercial departure-time categories.

## Airline mapping

The production advisor retains the raw ICAO operator code in the activity fact.

Airline identification is applied downstream through:

`aeropulse_operator_airline_reference`

and the view:

`vw_aeropulse_advisor_airline_month`

This layer adds the corresponding airline name and calculates:

- monthly activity share
- Morning activity percentage
- Afternoon activity percentage
- Evening activity percentage
- Night activity percentage

## Scoring pipeline

The activity data feeds the Advisor scoring layers.

The main scoring components include:

- monthly service/activity strength
- service consistency
- route-airline strength
- observed time-period fit
- price evidence, where sufficiently reliable

These components are combined in the downstream Advisor scoring and recommendation views.

The final recommendation layer produces an advisor score, recommendation level, and recommendation reason for the selected route, month, and preferred activity period.

## Data provenance

The historical 12-month population of:

`fact_aeropulse_advisor_airline_month`

was created during the earlier AeroPulse OPDI data-preparation workflow.

The original population script for this physical aggregate is not currently preserved in the repository. Therefore, the repository documents the production aggregate and its downstream transformation logic without presenting a newly reconstructed population query as the original implementation.

The current BigQuery table:

`fact_opdi_flights`

should not be treated as a complete reproduction source for the historical advisor aggregate because its current contents represent only the July 2026 OPDI slice.

## Interpretation

AeroPulse uses OPDI as an **observed flight-activity dataset**.

The Advisor therefore describes observed route and airline activity patterns rather than:

- scheduled airline timetables
- passenger demand
- market share
- revenue or profitability
- live flight status
- measured delay or cancellation performance

Price information is treated as a separate evidence layer and is not presented as live market pricing.