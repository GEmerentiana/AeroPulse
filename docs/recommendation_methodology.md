# AeroPulse — Recommendation Methodology

## 1. Purpose

The AeroPulse recommendation engine converts multiple aviation activity indicators into a transparent score.

The objective is to identify airlines and/or routes that demonstrate strong observed performance within the selected analysis period.

The recommendation engine is designed for analytical transparency rather than black-box prediction.

---

# 2. Important Limitation

AeroPulse recommendations are based on the data actually available to the project.

The recommendation should not be interpreted as:

* financial advice
* investment advice
* airline profitability ranking
* passenger demand ranking
* guaranteed future performance

Observed flight activity is not equivalent to passenger demand or revenue.

---

# 3. Recommendation Dimensions

The standard recommendation framework uses seven components.

| Component               |   Weight |
| ----------------------- | -------: |
| Activity / Demand Proxy |      25% |
| Route Strength          |      20% |
| Network Connectivity    |      15% |
| Growth                  |      15% |
| Seasonality             |      10% |
| Activity Consistency    |      10% |
| Weather Context         |       5% |
| **Total**               | **100%** |

---

# 4. Activity / Demand Proxy

### Weight

25%

### Purpose

Measures the level of observed flight activity associated with the airline or route.

Possible measures:

* total observed flights
* average monthly flights
* airport activity
* route activity

### Interpretation

This is an activity proxy.

It must not be described as actual passenger demand unless passenger data is available.

---

# 5. Route Strength

### Weight

20%

Possible indicators:

* route volume
* route share
* frequency
* route consistency
* route growth

A strong route is one that demonstrates meaningful and consistent observed activity.

---

# 6. Network Connectivity

### Weight

15%

Possible indicators:

* number of unique destinations
* number of unique routes
* airport coverage
* destination diversity

The metric rewards broader observed network presence.

---

# 7. Growth

### Weight

15%

Growth measures the change in observed activity over time.

Possible comparisons:

* month-over-month
* quarter-over-quarter
* year-over-year

The comparison period must be sufficiently complete before a growth metric is calculated.

---

# 8. Seasonality

### Weight

10%

Seasonality evaluates how observed activity changes across:

* months
* seasons
* holidays
* weekdays

A strong score may indicate strong activity during strategically important periods.

---

# 9. Activity Consistency

### Weight

10%

Consistency measures whether observed activity remains relatively stable over time.

Possible implementation:

1. Calculate monthly activity.
2. Calculate the mean.
3. Calculate variation around the mean.
4. Convert the result to a 0–100 score.

A more consistent activity pattern receives a higher score.

This is an operational activity consistency metric, not a formal airline reliability measure.

---

# 10. Weather Context

### Weight

5%

Weather can be used as contextual information.

Potential variables:

* precipitation
* wind
* temperature
* weather conditions

The weather component should only be activated if:

1. sufficient historical weather data exists;
2. airport locations can be matched correctly;
3. the relationship calculation is reproducible.

If these requirements are not satisfied, the weather component is excluded and the other weights are re-normalized.

---

# 11. Normalization

Raw metrics have different units.

For example:

```text
Flight volume = 10,000
Growth = 12%
Route count = 43
```

Therefore, each component is normalized to a 0–100 scale.

A simple min-max approach is:

```text
normalized_score =
    (value - minimum)
    /
    (maximum - minimum)
    × 100
```

If:

```text
maximum = minimum
```

the metric receives a neutral score or is excluded according to the implementation rule.

---

# 12. Direction of Metrics

Some metrics are positive when higher.

Examples:

* flight activity
* route volume
* network coverage
* growth

Some metrics may be negative when higher.

Examples:

* delays
* cancellation rate
* volatility

For negative metrics, the normalized score must be reversed.

Example:

```text
reversed_score = 100 - normalized_score
```

However, delay and cancellation metrics are only used if reliable source data exists.

---

# 13. Final Score

The standard score is:

```text
score =
    activity_score * 0.25
  + route_strength_score * 0.20
  + network_score * 0.15
  + growth_score * 0.15
  + seasonality_score * 0.10
  + consistency_score * 0.10
  + weather_score * 0.05
```

The result is between 0 and 100.

---

# 14. Recommendation Categories

The dashboard may use:

| Score  | Interpretation        |
| ------ | --------------------- |
| 80–100 | Strong recommendation |
| 65–79  | Good recommendation   |
| 50–64  | Moderate              |
| 35–49  | Weak                  |
| 0–34   | Low                   |

These categories are descriptive rather than predictive.

---

# 15. Recommendation Explanation

Every recommendation must be explainable.

Example:

> Airline A received a score of 84 because it demonstrated strong observed flight activity, broad route coverage, positive recent growth and consistent monthly activity.

The dashboard should expose the component scores so users can understand why the recommendation was produced.

---

# 16. Data Availability

The recommendation engine must track which components are supported by actual data.

Example:

```text
Activity              Available
Route Strength        Available
Network               Available
Growth                Available
Seasonality            Available
Consistency            Available
Weather                Unavailable
```

When a component is unavailable, the score is recalculated using the available components.

The remaining weights must be re-normalized so that the final score remains on a 0–100 scale.

---

# 17. Recommendation Transparency

AeroPulse does not use an unexplained machine-learning model for the final recommendation.

The score is rule-based and reproducible.

The user should be able to answer:

1. What was the score?
2. Which factors contributed to it?
3. What was the weight of each factor?
4. What data supported the factor?
5. Which factors were unavailable?

---

# 18. Recommended Output

The final recommendation view should contain:

* Airline/route
* Recommendation score
* Recommendation category
* Activity score
* Route strength score
* Network score
* Growth score
* Seasonality score
* Consistency score
* Weather score where available
* Explanation
* Data availability note
* Analysis period

---

# 19. Final Principle

The AeroPulse recommendation engine follows one central principle:

> **Use the strongest evidence available, make the calculation transparent, and never present unavailable data as if it existed.**
