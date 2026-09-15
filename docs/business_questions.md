# AeroPulse — Business Questions

## 1. Purpose

The AeroPulse dashboard is designed to answer practical business questions about aviation activity, airline networks and route performance.

The questions are structured around the data that can be reliably obtained from open and public sources.

The project prioritizes analytical credibility over unsupported KPIs.

---

# 2. Primary Business Question

> **Which airlines, airports and routes demonstrate the strongest observed aviation activity and network characteristics within the selected analysis period?**

This is the central question of AeroPulse.

The answer is generated from observed flight activity, route strength, network coverage, growth and seasonality.

---

# 3. Airport Performance Questions

## Q1. Which of the five German airports has the highest observed flight activity?

Target airports:

* Frankfurt (FRA)
* Munich (MUC)
* Berlin Brandenburg (BER)
* Düsseldorf (DUS)
* Hamburg (HAM)

### Metrics

* Total observed flights
* Monthly observed flights
* Growth
* Domestic/international activity where available

---

## Q2. How does flight activity differ between the five airports?

Compare:

* total activity
* monthly activity
* route count
* destination count
* airline count

### Business value

This identifies which airports demonstrate the strongest observed network activity.

---

## Q3. Which airports have the broadest observed network?

Measure:

* unique routes
* unique destinations
* unique airlines

### Business value

A broader network may indicate greater connectivity and strategic importance.

---

# 4. Airline Performance Questions

## Q4. Which target airlines have the highest observed flight activity?

Target airlines:

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

### Metrics

* observed flights
* monthly activity
* airport coverage
* route coverage
* destination count

---

## Q5. Which airlines have the broadest observed network?

Compare:

* unique routes
* unique destinations
* airports served/observed

### Business value

This identifies airlines with a broader observed network within the project scope.

---

## Q6. Which airlines show the strongest recent growth?

Compare observed activity across comparable periods.

### Metrics

* month-over-month growth
* quarter-over-quarter growth where appropriate
* year-over-year growth where sufficient history exists

### Business value

Identifies airlines whose observed activity is increasing.

---

## Q7. Which airlines demonstrate the most consistent activity?

Measure the stability of monthly observed flight activity.

### Business value

Identifies airlines with relatively stable observed activity rather than highly irregular activity.

### Important limitation

This is an **activity consistency** measure.

It must not be described as formal airline reliability unless reliable delay and cancellation data is available.

---

# 5. Route Performance Questions

## Q8. Which routes have the highest observed flight volume?

Identify the strongest routes associated with the five target airports.

### Metrics

* observed flights
* monthly activity
* airline count
* route growth

---

## Q9. Which routes demonstrate the strongest growth?

Compare route activity across comparable periods.

### Business value

Identifies routes that are becoming more active within the observed dataset.

---

## Q10. Which routes have the greatest airline competition?

Measure the number of airlines associated with each route.

### Business value

This can identify:

* highly competitive routes
* routes dominated by one airline
* potential market opportunities

---

## Q11. Which routes are highly concentrated?

Measure the proportion of route activity associated with each airline.

### Example

If:

```text
Airline A = 80%
Airline B = 15%
Airline C = 5%
```

the route is highly concentrated.

### Business value

This helps identify routes with strong incumbent presence versus more competitive routes.

---

# 6. Network Questions

## Q12. Which airlines have the strongest network presence at each airport?

Compare airlines by:

* observed flights
* routes
* destinations
* activity share

---

## Q13. Which airports are most connected to European destinations?

Measure:

* unique European destinations
* route count
* observed flight volume

---

## Q14. Which airlines have the greatest destination diversity?

Measure:

```text
COUNT(DISTINCT destination_iata)
```

### Business value

Identifies airlines with broader observed destination coverage.

---

# 7. Seasonality Questions

## Q15. Which months have the highest observed flight activity?

Analyze activity by month.

### Business value

Identifies high-activity and low-activity periods.

---

## Q16. How does activity change by season?

Compare:

* winter
* spring
* summer
* autumn

The season mapping is maintained in:

`config/seasons.csv`

---

## Q17. How does activity change during holidays?

Compare observed activity:

* during holidays
* outside holidays

### Business value

Helps identify seasonal demand/activity patterns.

### Important limitation

Observed flight activity is not the same as passenger demand.

---

## Q18. Which weekdays have the highest observed flight activity?

Compare:

* Monday
* Tuesday
* Wednesday
* Thursday
* Friday
* Saturday
* Sunday

### Business value

Identifies recurring weekly activity patterns.

---

# 8. Growth Questions

## Q19. Which airports show the strongest growth?

Calculate activity growth for each airport.

---

## Q20. Which airlines show the strongest growth?

Calculate activity growth for each airline.

---

## Q21. Which routes show the strongest growth?

Calculate activity growth for individual routes.

---

## Q22. Is growth broad-based or concentrated?

Determine whether growth comes from:

* many airlines
* many routes
* one major airline
* a small number of routes

### Business value

This distinguishes broad network expansion from isolated activity increases.

---

# 9. Airline Category Questions

## Q23. How does observed activity compare between legacy and low-cost airlines?

Compare:

### Legacy

* Lufthansa
* Air France
* KLM
* British Airways

### Low-cost

* Ryanair
* easyJet
* Wizz Air
* Eurowings

### Metrics

* observed flights
* routes
* destinations
* growth
* airport presence

### Business value

Provides a high-level comparison of airline business models within the selected scope.

---

# 10. Fare Questions

Fare analysis is conditional on the availability of a suitable historical public fare dataset.

## Q24. Which routes have the lowest observed fares?

Only answer if validated historical fare data is available.

---

## Q25. How do observed fares vary by route?

Compare:

* average fare
* median fare
* fare range

Only compatible currencies should be compared directly.

---

## Q26. How do observed fares change over time?

Analyze historical fare observations by:

* month
* route
* airline where available

---

## Q27. Which airlines have lower observed fares on comparable routes?

Only answer where:

1. airline information exists;
2. sufficient fare observations exist;
3. the comparison is made using comparable routes and conditions.

### Important limitation

An observed fare is not necessarily the final price paid by a passenger.

It may also not represent a currently bookable fare.

---

# 11. Operational Performance Questions

These questions are conditional on reliable scheduled/actual operational data.

## Q28. Which airlines have the lowest average departure delay?

Only calculate if reliable departure-delay data exists.

---

## Q29. Which airlines have the lowest average arrival delay?

Only calculate if reliable arrival-delay data exists.

---

## Q30. Which airlines have the lowest cancellation rate?

Only calculate if reliable cancellation data exists.

If cancellation data is unavailable, the dashboard must display:

> Not available with current source.

It must not display zero.

---

# 12. Weather Context Questions

Weather analysis is optional.

## Q31. Does observed flight activity change during adverse weather conditions?

Potential variables:

* precipitation
* wind
* temperature
* weather conditions

### Important limitation

This analysis identifies associations.

It does not prove that weather caused changes in flight activity.

---

## Q32. Which airports show the greatest activity variation during different weather conditions?

Compare observed activity under defined weather categories.

This is an exploratory analysis rather than a causal model.

---

# 13. Recommendation Questions

## Q33. Which airline receives the highest AeroPulse recommendation score?

The score combines:

* activity
* route strength
* network connectivity
* growth
* seasonality
* activity consistency
* weather context where available

---

## Q34. Why was an airline recommended?

The dashboard must show the factors contributing to the score.

For example:

```text
Airline A

Activity              92
Route Strength        88
Network               84
Growth                79
Seasonality           75
Consistency            90
Weather Context       70

Final Score            85
```

The exact values will be calculated from the validated dataset.

---

## Q35. Which routes receive the strongest recommendation?

Routes can be ranked using:

* observed volume
* growth
* route consistency
* network importance
* competition
* seasonality

---

## Q36. Which factors have the greatest influence on the recommendation?

The dashboard should make the component scores visible.

This prevents the recommendation from becoming a black-box result.

---

# 14. Data Freshness Questions

## Q37. How recent is the available aviation data?

The dashboard must show:

* latest available source date
* earliest available source date
* analysis start date
* analysis end date
* last successful refresh

---

## Q38. Is the dashboard based on a complete 12-month period?

The analysis window is calculated from the latest available source date.

### Formula

```text
analysis_end_date = latest_available_date

analysis_start_date =
    latest_available_date - 12 months
```

This ensures that the analysis is based on the source's actual coverage.

---

# 15. Data Quality Questions

## Q39. How complete is the underlying dataset?

Monitor:

* missing values
* invalid airport codes
* invalid airline codes
* duplicate records
* date coverage

---

## Q40. Which analytical fields are unavailable?

The dashboard/documentation should clearly identify fields that are not supplied by the selected source.

Examples:

* scheduled flight time
* commercial fare
* passenger count
* cancellation reason

---

# 16. Questions AeroPulse Does Not Claim to Answer

The following questions are outside the reliable scope of the core project unless additional validated data is introduced:

### Revenue

> Which airline generates the most revenue?

Not supported without revenue data.

### Profitability

> Which airline is the most profitable?

Not supported without financial data.

### Passenger demand

> Which airline has the highest passenger demand?

Observed flight activity is not equivalent to passenger demand.

### Market share

> Which airline has the largest passenger market share?

Not supported without appropriate passenger/market data.

### Guaranteed reliability

> Which airline is the most reliable?

Not supported solely by flight-tracking activity.

### Cancellations

> Which airline has the lowest cancellation rate?

Only supported when reliable cancellation data is available.

### Historical pricing

> Which airline was always cheapest?

Not supported without sufficiently complete historical fare data.

---

# 17. Priority Business Questions

For the final dashboard, the highest-priority questions are:

1. Which airport has the highest observed activity?
2. Which airline has the highest observed activity?
3. Which routes are strongest?
4. Which airlines have the broadest networks?
5. Which routes and airlines show the strongest growth?
6. Which airports/routes are most connected?
7. How does activity change by month and season?
8. Which routes have the strongest competition?
9. Which airline receives the highest AeroPulse recommendation score?
10. Why does the recommendation engine select that airline or route?

---

# 18. Final Business Objective

AeroPulse transforms open aviation data into an actionable analytical framework.

The final dashboard should allow a user to move from:

```text
What is happening?
        ↓
Where is it happening?
        ↓
Which airlines/routes are involved?
        ↓
How is activity changing?
        ↓
What patterns exist?
        ↓
Which option scores highest?
        ↓
Why?
```

The recommendation must always be traceable back to measurable data and documented methodology.
