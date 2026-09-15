# AeroPulse — Data Source Evaluation

## 1. Purpose

This document evaluates potential data sources for the AeroPulse Aviation Performance & Recommendation Dashboard.

The project originally considered commercial aviation APIs. Because the project is designed as a portfolio project with a zero-cost or near-zero-cost data strategy, the current implementation prioritizes publicly available and open data sources.

The source strategy must satisfy the following requirements:

* Aviation data must cover European aviation where possible.
* The five target German airports must be supported:

  * Frankfurt (FRA)
  * Munich (MUC)
  * Berlin Brandenburg (BER)
  * Düsseldorf (DUS)
  * Hamburg (HAM)
* The project must support the eight target airlines where data is available:

  * Lufthansa
  * Air France
  * KLM
  * British Airways
  * Ryanair
  * easyJet
  * Wizz Air
  * Eurowings
* Data must be suitable for historical analysis.
* Data must be legally and technically usable for a portfolio project.
* Data limitations must be documented rather than hidden.

---

## 2. Source Strategy

AeroPulse uses a multi-source architecture rather than depending on a single commercial aviation API.

### Primary aviation activity source

**OpenSky Network**

OpenSky provides aviation surveillance data based primarily on ADS-B and Mode-S observations.

It is suitable for:

* observed aircraft activity
* flight movements
* aircraft identifiers
* airport activity
* route/network analysis
* temporal aviation activity analysis

OpenSky does not provide all commercial schedule information.

In particular, the project must not assume that OpenSky provides:

* complete scheduled flight schedules
* commercial ticket prices
* passenger counts
* reliable cancellation reasons
* complete scheduled-versus-actual delay information

Therefore, those fields are optional and must only be populated when a separate validated source provides them.

---

## 3. Airport Reference Data

### OurAirports

OurAirports is used as a potential airport reference-data source.

Potential fields include:

* airport name
* IATA code
* ICAO code
* latitude
* longitude
* country
* airport type

The airport reference dataset supports the AeroPulse airport dimension.

The five core airports are:

| Airport                    | IATA | ICAO | Country |
| -------------------------- | ---- | ---- | ------- |
| Frankfurt Airport          | FRA  | EDDF | Germany |
| Munich Airport             | MUC  | EDDM | Germany |
| Berlin Brandenburg Airport | BER  | EDDB | Germany |
| Düsseldorf Airport         | DUS  | EDDL | Germany |
| Hamburg Airport            | HAM  | EDDH | Germany |

---

## 4. Weather Data

### Open-Meteo

Open-Meteo is an optional supporting source.

It can provide historical weather variables such as:

* temperature
* precipitation
* wind
* weather conditions

Weather data is not treated as direct proof of flight disruption.

Instead, it is used as contextual information that can help investigate relationships between weather conditions and observed aviation activity.

Example analysis:

> Does observed flight activity differ during periods of heavy precipitation or strong wind?

Any relationship identified in the dashboard must be described as an association rather than proof of causation.

---

## 5. Fare Data

Historical commercial airfare data is significantly more difficult to obtain from free public APIs than flight-tracking data.

AeroPulse therefore follows a strict rule:

> No historical fare values will be fabricated or simulated and presented as real observations.

A free/public airfare dataset will only be included if it provides sufficient information for meaningful analysis.

Potential minimum requirements include:

* observation date
* origin
* destination
* price
* currency
* airline where available

Additional useful fields include:

* travel date
* cabin class
* number of stops
* advance purchase period

If no sufficiently reliable public fare source is identified, the airfare component will be marked as unavailable rather than replacing it with invented data.

---

## 6. Commercial Sources Considered

Commercial sources were evaluated during project planning.

### Aviation Edge

Aviation Edge was considered because it provides historical flight information including operational fields.

However, it was rejected for the current implementation because the available API access requires a paid subscription.

It is therefore not a dependency of the final AeroPulse project.

### OAG

OAG provides extensive commercial aviation datasets, including historical schedules and airfare-related data.

It is suitable for enterprise-level aviation analytics but is not required for the zero-cost portfolio implementation.

### FlightAware AeroAPI

FlightAware provides aviation data through a commercial API.

It is not used as the primary AeroPulse source because the project is designed to minimize paid data dependencies.

### Cirium

Cirium provides extensive historical aviation datasets.

It is not used because commercial access is outside the intended project scope.

---

## 7. Source Selection

The current source-selection decision is:

| Data requirement         | Preferred source            | Status          |
| ------------------------ | --------------------------- | --------------- |
| Observed flight activity | OpenSky                     | Selected        |
| Airport reference data   | OurAirports                 | Selected        |
| Weather context          | Open-Meteo                  | Optional        |
| Public holidays          | Open/public calendar data   | To be prepared  |
| Historical fares         | Public dataset if suitable  | To be evaluated |
| Commercial schedules     | Not required for core model | Not selected    |
| Passenger volumes        | Not required for core model | Not selected    |

---

## 8. Data Quality Principles

Every source must pass the following checks before entering the analytical layer.

### Completeness

Check:

* required columns
* missing values
* date coverage
* airport coverage
* airline coverage

### Validity

Check:

* valid IATA/ICAO codes
* valid dates
* valid timestamps
* valid numeric values
* valid geographic coordinates

### Uniqueness

Check for duplicate observations.

### Consistency

Check that:

* airport codes map correctly
* airline codes map correctly
* dates are logically ordered
* origin and destination are valid

### Freshness

Record:

* latest source date
* earliest source date
* extraction timestamp
* last successful pipeline run

---

## 9. Important Data Limitation

AeroPulse must distinguish between:

### Observed activity

Information directly supported by the aviation tracking data.

### Scheduled operations

Information requiring a schedule source.

### Commercial performance

Information requiring commercial data such as ticket prices, passenger numbers or revenue.

These categories must not be mixed.

For example:

> High observed flight activity does not automatically mean high passenger demand.

Therefore, AeroPulse uses careful terminology such as:

* observed flight activity
* observed route volume
* network strength
* observed airline activity

instead of making unsupported claims about revenue or passenger demand.

---

## 10. Final Decision

The final AeroPulse architecture prioritizes:

1. OpenSky for aviation activity.
2. OurAirports for airport reference data.
3. Open-Meteo for optional weather context.
4. Public holiday data for seasonality.
5. A validated public fare dataset only if one can be identified.

The project will not depend on Aviation Edge.

All source limitations will be documented in the final portfolio and presentation.
