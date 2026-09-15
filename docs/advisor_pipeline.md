# AeroPulse Flight Choice Advisor — Production Pipeline

## Overview

The Flight Choice Advisor is a rule-based recommendation pipeline that evaluates observed airline activity for a selected route, month, and preferred activity period.

The production pipeline combines historical OPDI flight-observation data with airline mapping, service consistency, observed time-period fit, and price evidence where sufficiently reliable.

The pipeline is designed to be transparent, reproducible, and explainable.

---

## 1. Source Data

The underlying aviation activity data comes from the OpenSky Network's Open Data for Performance and Infrastructure (OPDI).

AeroPulse uses a historical observation window covering:

**August 2025 – July 2026**

OPDI records represent observed/reconstructed flight activity derived from ADS-B data.

They should not be interpreted as:

- scheduled airline timetables
- passenger demand
- market share
- revenue or profitability
- live flight status
- measured delay or cancellation performance

---

## 2. Advisor Activity Fact

The production Advisor uses the BigQuery table:

`aeropulse-aviation.aviation_performance.fact_aeropulse_advisor_airline_month`

Its grain is:

**route × month × ICAO operator**

The table contains:

- departure airport (`adep`)
- arrival airport (`ades`)
- observation month (`month`)
- ICAO operator (`icao_operator`)
- observed flight count
- Morning activity
- Afternoon activity
- Evening activity
- Night activity

Current production coverage:

- **11,842 rows**
- **2,838 route-month combinations**
- **269,452 observed flights**
- **August 2025 – July 2026**

---

## 3. Airline Mapping

The activity fact retains the original ICAO operator code.

Airline identification is applied through:

`aeropulse_operator_airline_reference`

The downstream view:

`vw_aeropulse_advisor_airline_month`

adds the mapped airline name and calculates:

- monthly activity share
- Morning activity percentage
- Afternoon activity percentage
- Evening activity percentage
- Night activity percentage

This separates the raw aviation operator identifier from the analytical airline label.

---

## 4. Route and Month Layer

The view:

`vw_aeropulse_advisor_route_month`

adds route-level information required by the dashboard.

This includes:

- route identifier
- origin IATA
- destination IATA
- origin city
- destination city
- origin country
- destination country
- route type
- route display label

The route type distinguishes:

- Domestic: Germany → Germany
- International: Germany → non-Germany

---

## 5. Monthly Activity Strength

The view:

`vw_aeropulse_advisor_activity_strength`

classifies observed monthly activity into strength levels.

The current rule is:

| Observed flights | Classification | Score |
|---:|---|---:|
| 0–4 | Limited | 20 |
| 5–17 | Moderate | 40 |
| 18–48 | Strong | 70 |
| >48 | Very Strong | 100 |

This measures observed flight activity rather than passenger demand.

---

## 6. Service Consistency

The view:

`vw_aeropulse_advisor_consistency`

evaluates how consistently an airline operates on a route across the 12-month observation window.

The current rule is:

| Active months | Classification | Score |
|---:|---|---:|
| 0–2 | Very Limited | 20 |
| 3–5 | Seasonal | 40 |
| 6–8 | Established | 60 |
| 9–11 | Highly Consistent | 80 |
| 12 | Year-Round | 100 |

This is an observed activity consistency measure.

It is not a formal airline reliability metric.

---

## 7. Monthly Service Score

The view:

`vw_aeropulse_advisor_monthly_service`

combines activity strength and service consistency.

The formula is:

```text
monthly_service_score =
    activity_strength_score × 0.60
  + service_consistency_score × 0.40
```

The monthly service score is therefore based on both the strength of observed activity and the consistency of route-airline activity.

---

## 8. Route-Airline Strength

The view:

`vw_aeropulse_advisor_route_airline_score`

aggregates route-airline activity across the available months.

The current formula is:

```text
route_airline_score =
    average_activity_strength_score × 0.60
  + service_consistency_score × 0.40
```

This provides a broader route-airline activity signal alongside the selected month's service score.

---

## 9. Observed Time-Period Fit

The Advisor uses four broad observed activity periods:

- Morning
- Afternoon
- Evening
- Night

The views:

`vw_aeropulse_advisor_detailed_time_activity`

`vw_aeropulse_advisor_detailed_time_fit`

and

`vw_aeropulse_advisor_selected_time`

translate observed activity percentages into a time-period fit score.

The current thresholds are:

| Activity share | Classification | Score |
|---:|---|---:|
| ≥50% | Very Strong | 100 |
| ≥35% | Strong | 80 |
| ≥20% | Moderate | 60 |
| ≥10% | Limited | 40 |
| <10% | Very Limited | 20 |

These periods describe **when flight activity was observed in the OPDI data**.

They should not be interpreted as scheduled commercial departure-time categories.

---

## 10. Price Evidence

Price is treated as a separate evidence layer.

The production price pipeline uses:

`fact_route_price_observations_production`

and the downstream views:

- `vw_route_airline_price_production`
- `vw_aeropulse_advisor_price_score`
- `vw_aeropulse_advisor_price_reliability`
- `vw_aeropulse_advisor_price_evidence`

Price competitiveness is calculated relative to the lowest observed average airline price for the same route.

Price sample quality is classified as:

| Observations | Quality |
|---:|---|
| ≥10 | Strong Sample |
| 3–9 | Moderate Sample |
| 1–2 | Limited Sample |

Price evidence is therefore used only when observations are available and sufficiently reliable.

The AeroPulse price layer must not be presented as live market pricing.

---

## 11. Final Advisor Score

The production final scoring view is:

`vw_aeropulse_advisor_final_score_v3`

The standard weighting is:

| Component | Weight |
|---|---:|
| Monthly service score | 35% |
| Observed time-period fit | 25% |
| Route-airline strength | 25% |
| Price evidence | 15% |

When reliable price evidence exists:

```text
advisor_score =
    monthly_service_score × 0.35
  + time_fit_score × 0.25
  + route_airline_score × 0.25
  + reliable_price_score × 0.15
```

When reliable price evidence is unavailable, the non-price components are normalized so that missing price data does not penalize the recommendation.

The final score is reported on a 0–100 scale.

---

## 12. Recommendation Layer

The view:

`vw_aeropulse_advisor_recommendation_v2`

converts the final score into a recommendation category.

| Advisor score | Recommendation |
|---:|---|
| ≥80 | Excellent Choice |
| ≥70 | Strong Choice |
| ≥60 | Good Choice |
| ≥50 | Consider |
| <50 | Lower Priority |

The recommendation layer also generates a human-readable recommendation reason.

Ranking is performed within the selected:

**route × month × preferred time**

scenario.

---

## 13. Dashboard Output

The production dashboard view is:

`vw_aeropulse_flight_choice_dashboard`

It combines the recommendation output with route metadata.

The dashboard provides:

- origin
- destination
- travel month
- preferred activity period
- airline
- Advisor score
- recommendation level
- recommendation reason
- monthly service score
- time-period fit score
- route-airline score
- price evidence
- price sample quality

The production view keeps the recommendation logic in BigQuery while allowing Looker Studio to focus on presentation and user interaction.

---

## 14. Pipeline Flow

The production logic can be summarized as:

```text
Historical OPDI observations
            │
            ▼
Advisor activity fact
(route × month × ICAO operator)
            │
            ▼
Airline mapping
            │
            ▼
Route + month enrichment
            │
            ├──────────────► Monthly activity strength
            │
            ├──────────────► Service consistency
            │                         │
            │                         ▼
            │                 Monthly service score
            │
            ├──────────────► Observed time-period fit
            │
            ├──────────────► Route-airline strength
            │
            └──────────────► Price evidence
                                      │
                                      ▼
                           Final Advisor Score
                                      │
                                      ▼
                           Recommendation Level
                                      │
                                      ▼
                         Dashboard Recommendation
```

---

## 15. Reproducibility and Provenance

The downstream Advisor SQL transformations are preserved in the repository under:

`sql/`

The pipeline documents the production transformation logic from the advisor activity fact through to the final dashboard view.

The historical 12-month population of:

`fact_aeropulse_advisor_airline_month`

was created during the earlier AeroPulse OPDI data-preparation workflow.

The original population script for this physical aggregate is not currently preserved in the repository.

Therefore, the repository documents the production aggregate and its downstream transformation logic without presenting a newly reconstructed population query as the original implementation.

The current BigQuery table:

`fact_opdi_flights`

should not be treated as a complete reproduction source for the historical Advisor aggregate because its current contents represent only the July 2026 OPDI slice.

---

## 16. Interpretation

The Flight Choice Advisor is a **decision-support model based on observed aviation activity**.

Its recommendations answer a question such as:

> Which airline appears to be the strongest observed option for this route, month, and preferred activity period, based on the available AeroPulse evidence?

It does not claim to predict:

- passenger demand
- future airline performance
- ticket prices
- delays or cancellations
- profitability
- customer satisfaction

The model is intentionally rule-based and transparent so that each recommendation can be traced back to observable inputs and explicit scoring rules.
