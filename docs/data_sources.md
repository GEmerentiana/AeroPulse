# AeroPulse — Data Sources

## 1. Overview

AeroPulse uses multiple data sources to create an aviation performance and recommendation analytics pipeline.

The architecture separates:

* aviation activity data
* airport reference data
* weather data
* calendar/holiday data
* optional fare data

This prevents the project from depending on one commercial API.

---

## 2. OpenSky Network

### Role

Primary source for observed aviation activity.

### Main use

OpenSky data can support:

* aircraft observations
* flight activity
* airport activity
* route activity
* airline activity where the relevant identification is available
* temporal aviation analysis

### Important limitation

OpenSky is a flight-tracking/surveillance source rather than a commercial airline schedule database.

Therefore, AeroPulse must not assume that OpenSky provides:

* complete scheduled flight times
* ticket prices
* passenger numbers
* revenue
* complete cancellation information
* complete commercial delay information

### AeroPulse usage

OpenSky data is transformed into the flight activity layer and eventually into:

`fact_flights`

---

## 3. OurAirports

### Role

Airport reference data.

### Main use

Used to enrich airport codes with:

* airport name
* IATA
* ICAO
* country
* latitude
* longitude
* airport type

### AeroPulse usage

The cleaned airport reference data becomes:

`dim_airport`

---

## 4. Open-Meteo

### Role

Optional weather context.

### Main use

Potential variables:

* temperature
* precipitation
* wind
* weather conditions

### AeroPulse usage

Weather may be stored in a separate weather dataset or integrated into an analytical layer if required.

Weather is contextual and does not independently establish the cause of flight changes.

---

## 5. Public Holiday Data

### Role

Seasonality and holiday analysis.

### Main use

Identify:

* public holidays
* holiday periods
* holiday type
* country
* date

### AeroPulse usage

Holiday information will support:

`dim_date`

and the seasonality/holiday analysis.

Germany is the primary country of interest.

---

## 6. Historical Fare Data

### Role

Optional price analysis.

### Requirement

A fare dataset will only be included if the source provides real historical observations with enough information for analysis.

Minimum useful fields:

* observation date
* origin
* destination
* price
* currency

Preferred fields:

* airline
* travel date
* cabin
* stops
* advance purchase period

### Important rule

AeroPulse will never create artificial historical fare observations and present them as real-world data.

If a suitable public source is unavailable, the airfare component will remain optional.

---

## 7. Target Airports

AeroPulse focuses on five German airports.

| Airport            | IATA | ICAO |
| ------------------ | ---- | ---- |
| Frankfurt          | FRA  | EDDF |
| Munich             | MUC  | EDDM |
| Berlin Brandenburg | BER  | EDDB |
| Düsseldorf         | DUS  | EDDL |
| Hamburg            | HAM  | EDDH |

---

## 8. Target Airlines

### Legacy / Full-Service

* Lufthansa
* Air France
* KLM
* British Airways

### Low-Cost

* Ryanair
* easyJet
* Wizz Air
* Eurowings

Airline codes are maintained in:

`config/airlines.csv`

---

## 9. Source Hierarchy

The project follows this hierarchy:

```text
Source
    ↓
Raw data
    ↓
Validation
    ↓
Processed data
    ↓
BigQuery
    ↓
SQL analytics
    ↓
Looker Studio
```

Raw data must remain separate from processed data.

---

## 10. Source Metadata

Each ingestion process should record:

* source name
* extraction timestamp
* earliest source date
* latest source date
* number of records retrieved
* number of records accepted
* number of records rejected
* pipeline status

This metadata supports data freshness reporting.

---

## 11. Data Freshness

AeroPulse reports the latest date actually available in the source.

The dashboard must not claim that data is current through today's date unless the source actually contains data through today's date.

The following dates should be displayed where appropriate:

* Latest available data date
* Analysis start date
* Analysis end date
* Last pipeline refresh

---

## 12. Data Governance

The project follows these principles:

* Do not fabricate data.
* Do not silently fill important missing values.
* Keep source data separate from processed data.
* Document source limitations.
* Preserve source identifiers where available.
* Record ingestion timestamps.
* Validate before loading into BigQuery.