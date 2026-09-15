# AeroPulse — KPI Definitions

## 1. Purpose

This document defines the metrics used by AeroPulse.

KPIs are divided into:

1. Core KPIs
2. Conditional KPIs
3. Recommendation metrics

Conditional KPIs are only calculated when the necessary source data exists.

---

# 2. Core KPIs

## Total Observed Flights

### Definition

Number of valid flight/activity observations in the selected analysis period.

### Formula

```text
COUNT(valid flight observations)
```

---

## Flights by Airline

### Definition

Number of observed flight/activity records associated with an airline.

### Formula

```text
COUNT(flight_id)
GROUP BY airline
```

---

## Flights by Airport

### Definition

Number of observed flight/activity records associated with an airport.

Depending on the analytical view, the airport may represent origin, destination or both.

---

## Route Volume

### Definition

Number of observed flight/activity records between an origin and destination.

### Formula

```text
COUNT(flight_id)
GROUP BY origin_iata, destination_iata
```

---

## Monthly Flight Activity

### Definition

Number of observed flights during a calendar month.

---

## Activity Growth

### Definition

Percentage change in observed flight activity between two comparable periods.

### Formula

```text
(current_period - previous_period)
/
previous_period
* 100
```

If the previous period equals zero, the growth rate is not calculated.

---

## Route Share

### Definition

Share of an airport's observed activity represented by a specific route.

### Formula

```text
route_activity
/
total_airport_activity
* 100
```

---

## Airline Network Coverage

### Definition

Number of unique routes served/observed for an airline within the selected scope.

### Formula

```text
COUNT(DISTINCT route_id)
```

---

## Destination Diversity

### Definition

Number of unique destinations associated with an airline or airport.

### Formula

```text
COUNT(DISTINCT destination_iata)
```

---

# 3. Seasonality KPIs

## Monthly Activity Index

### Definition

Monthly activity relative to the average monthly activity during the analysis period.

### Formula

```text
monthly_activity
/
average_monthly_activity
```

---

## Seasonal Activity

### Definition

Observed flight activity aggregated by season.

The season classification is maintained in:

`config/seasons.csv`

---

## Holiday Activity

### Definition

Observed flight activity during defined holiday periods.

Holiday classification is based on the holiday reference data.

---

# 4. Conditional Operational KPIs

These KPIs are only calculated when reliable scheduled/actual operational information is available.

## Average Departure Delay

```text
AVG(departure_delay_minutes)
```

---

## Average Arrival Delay

```text
AVG(arrival_delay_minutes)
```

---

## Delay Rate

```text
delayed_flights
/
eligible_flights
* 100
```

---

## Cancellation Rate

```text
cancelled_flights
/
eligible_flights
* 100
```

If cancellation information is unavailable, the KPI must be shown as unavailable rather than zero.

---

# 5. Conditional Fare KPIs

## Average Observed Fare

```text
AVG(price)
```

The calculation must only compare compatible currencies.

---

## Median Observed Fare

```text
MEDIAN(price)
```

or the equivalent BigQuery analytical implementation.

---

## Minimum Observed Fare

```text
MIN(price)
```

This should not be interpreted as a guaranteed bookable fare.

---

## Fare Trend

Percentage change in observed fare over comparable periods.

---

# 6. Recommendation Metrics

The recommendation score uses normalized analytical signals.

All component scores are converted to a 0–100 scale.

---

## Demand / Activity

Measures observed flight activity.

Weight:

**25%**

---

## Route Strength

Measures the strength of the routes associated with the airline.

Weight:

**20%**

---

## Network Connectivity

Measures breadth and connectivity of the observed network.

Weight:

**15%**

---

## Growth

Measures recent growth in observed activity.

Weight:

**15%**

---

## Seasonality

Measures consistency and strength of activity across relevant seasons.

Weight:

**10%**

---

## Operational Activity Consistency

Measures consistency of observed activity over time.

Weight:

**10%**

This should not be interpreted as formal airline reliability unless delay/cancellation data is available.

---

## Weather Context

Weight:

**5%**

Weather is an optional contextual signal.

If reliable weather-linked analysis is not available, this component may be excluded and the remaining weights must be re-normalized.

---

# 7. Recommendation Score

The general score is:

```text
Recommendation Score =
    Activity Score × 25%
  + Route Strength Score × 20%
  + Network Score × 15%
  + Growth Score × 15%
  + Seasonality Score × 10%
  + Consistency Score × 10%
  + Weather Context Score × 5%
```

All scores are normalized to 0–100.

---

# 8. Interpretation

The recommendation score indicates which airline or route has the strongest performance according to the defined analytical signals.

It does not represent:

* profitability
* revenue
* passenger satisfaction
* investment advice
* guaranteed future performance

---

# 9. Data Availability Rule

If a KPI cannot be calculated because the required source field is unavailable:

* do not substitute zero
* do not invent values
* do not estimate without documenting the method

Instead, mark the KPI as:

`Not available`

or

`Not supported by current source`

---

# 10. Freshness

All KPIs must use the defined AeroPulse analysis window.

The window is:

```text
analysis_end_date = latest available source date

analysis_start_date =
analysis_end_date - 12 months
```

The dashboard must display these dates.
