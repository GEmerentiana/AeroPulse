# AeroPulse — Data Requirements Checklist

## 1. Purpose

This checklist defines the minimum data requirements for the AeroPulse project.

A requirement is considered satisfied only when the necessary data is actually available and validated.

---

# 2. Airport Requirements

## Required

* [x] FRA — Frankfurt
* [x] MUC — Munich
* [x] BER — Berlin Brandenburg
* [x] DUS — Düsseldorf
* [x] HAM — Hamburg

## Airport reference fields

* [ ] Airport name
* [ ] IATA code
* [ ] ICAO code
* [ ] Country
* [ ] Latitude
* [ ] Longitude
* [ ] Airport type

---

# 3. Airline Requirements

## Target airlines

* [x] Lufthansa
* [x] Air France
* [x] KLM
* [x] British Airways
* [x] Ryanair
* [x] easyJet
* [x] Wizz Air
* [x] Eurowings

## Airline reference fields

* [ ] Airline name
* [ ] IATA code
* [ ] ICAO code
* [ ] Airline category

---

# 4. Flight Activity Requirements

## Core

* [ ] Flight/activity date
* [ ] Origin airport
* [ ] Destination airport
* [ ] Airline identification where available
* [ ] Aircraft identification where available
* [ ] Source identifier where available
* [ ] Source name
* [ ] Ingestion timestamp

## Optional

* [ ] Flight number
* [ ] Scheduled departure
* [ ] Actual departure
* [ ] Scheduled arrival
* [ ] Actual arrival
* [ ] Departure delay
* [ ] Arrival delay
* [ ] Cancellation
* [ ] Cancellation reason

Optional fields must only be populated when a source provides them.

---

# 5. Fare Requirements

## Minimum

* [ ] Observation date
* [ ] Origin
* [ ] Destination
* [ ] Price
* [ ] Currency

## Preferred

* [ ] Airline
* [ ] Travel date
* [ ] Cabin class
* [ ] Stops
* [ ] Advance purchase days

## Rule

No fare values may be invented or simulated and presented as historical observations.

---

# 6. Weather Requirements

Weather is optional.

Potential fields:

* [ ] Date
* [ ] Temperature
* [ ] Precipitation
* [ ] Wind speed
* [ ] Weather condition

Weather is contextual and should not be interpreted as proof of causation.

---

# 7. Holiday Requirements

* [ ] Holiday date
* [ ] Country
* [ ] Holiday name
* [ ] Holiday type

Germany is the primary country.

---

# 8. Date Requirements

The date dimension should eventually contain:

* date
* year
* quarter
* month
* month name
* week
* weekday
* weekday name
* weekend indicator
* season
* holiday indicator
* holiday name

---

# 9. Data Quality Requirements

## Completeness

* [ ] Required columns present
* [ ] Dates populated
* [ ] Airport codes populated where required
* [ ] Airline codes populated where available

## Validity

* [ ] Valid dates
* [ ] Valid airport codes
* [ ] Valid airline codes
* [ ] Valid numeric fields
* [ ] Valid timestamps

## Uniqueness

* [ ] Duplicate observations identified
* [ ] Duplicate handling documented
* [ ] Unique record identifier generated

## Consistency

* [ ] Origin and destination are valid
* [ ] Date fields are logically consistent
* [ ] Source identifiers preserved

---

# 10. Freshness Requirements

The pipeline must calculate:

* [ ] Earliest source date
* [ ] Latest source date
* [ ] Analysis start date
* [ ] Analysis end date
* [ ] Last extraction timestamp
* [ ] Last successful pipeline run

---

# 11. BigQuery Requirements

### Dimensions

* [ ] dim_airport
* [ ] dim_airline
* [ ] dim_route
* [ ] dim_date

### Facts

* [ ] fact_flights
* [ ] fact_airfares

### Analytics

* [ ] vw_flight_performance
* [ ] vw_route_performance
* [ ] vw_airline_performance
* [ ] vw_price_analysis
* [ ] vw_recommendations

Views that depend on unavailable source fields must not produce misleading results.

---

# 12. Dashboard Requirements

### Executive Overview

* [ ] Total observed flights
* [ ] Airport comparison
* [ ] Airline comparison
* [ ] Route activity
* [ ] Latest available date
* [ ] Analysis period

### Network

* [ ] Route volume
* [ ] Airport connectivity
* [ ] Airline route coverage

### Performance

* [ ] Airline activity
* [ ] Route activity
* [ ] Growth
* [ ] Optional delay/cancellation metrics

### Seasonality

* [ ] Monthly activity
* [ ] Seasonal activity
* [ ] Holiday activity
* [ ] Weekday patterns

### Recommendations

* [ ] Recommendation score
* [ ] Score components
* [ ] Explanation
* [ ] Confidence/data-availability note

---

# 13. Final Acceptance Rule

A feature is considered complete only when:

1. Required source data exists.
2. The data passes validation.
3. The calculation is reproducible.
4. The methodology is documented.
5. The dashboard does not overstate what the data represents.
