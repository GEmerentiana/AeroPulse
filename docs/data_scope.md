# AeroPulse — Data Scope

## Origin Airports

AeroPulse focuses on five major German airports:

- Frankfurt (FRA)
- Munich (MUC)
- Berlin Brandenburg (BER)
- Düsseldorf (DUS)
- Hamburg (HAM)

## Airlines

### Legacy Airlines

- Lufthansa
- Air France
- KLM
- British Airways

### Low-Cost Airlines

- Ryanair 
- easyJet
- Wizz Air
- Eurowings

The final airline identifiers must be verified against the selected aviation data source.

## Geography

Destination scope:

- Germany
- Europe

Excluded:

- destinations outside Europe
- origins outside the five selected German airports
- airlines outside the selected airline scope

## Analysis Period

A rolling 12-month period.

Conceptually:

analysis_start_date = DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)

analysis_end_date = CURRENT_DATE()

## Core Historical Performance

AeroPulse must analyze:

- Flight volume
- Ticket price
- Delays
- Cancellations
- Growth
- Route strength
- Seasonality
- Public holidays

## Required Data Fields

The selected data source must provide, or allow a reliable join to:

- flight date
- departure time
- airline
- origin
- destination
- ticket/fare price
- delay information
- cancellation information

If ticket price is not available in the primary flight dataset, a compatible historical fare source must be investigated.

## Data Refresh

AeroPulse should be designed as a refreshable historical analytics pipeline.

The pipeline should be able to:

- retrieve newly available data
- validate incoming data
- add new records
- update historical performance metrics
- maintain a rolling 12-month analysis window
- update BigQuery analytical tables
- support dashboard refreshes

The exact refresh frequency will depend on the selected data source.

## Historical vs Real-Time

The initial AeroPulse version is a historical analytics solution.

It is not a live booking or real-time flight availability system.

Real-time flight status, live prices, current availability and weather intelligence are considered future extensions.