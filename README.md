# AeroPulse — Aviation Route Opportunity Intelligence

> Turning complex aviation information into smarter route, airline and flight decisions.

## Overview

AeroPulse is an aviation analytics and decision-support project that brings together route performance, airline activity, timing, fare observations and passenger-experience evidence to help answer a simple question:

**Which flight option makes the most sense — and why?**

Instead of looking at a single signal such as price, AeroPulse combines multiple evidence layers and presents them through an interactive Looker Studio dashboard.

The project is designed as an analytical prototype rather than a booking engine or predictive model.

---

## The Decision Challenge

Choosing a flight is rarely only about price.

Travelers may also consider:

- Which airline is strongest on the route?
- When are flights most active?
- How does the observed fare compare with alternatives?
- What do passengers report about the airline experience?
- Does the recommendation change for different traveler profiles?

AeroPulse brings these perspectives together into one decision-support environment.

---

## What AeroPulse Does

AeroPulse provides eight analytical dashboard pages:

1. **Welcome to AeroPulse**
2. **Executive Route Intelligence**
3. **Flight Choice Advisor**
4. **Route & Airline Deep Dive**
5. **Flight Timing Intelligence**
6. **Price & Market Intelligence**
7. **Passenger Experience Intelligence**
8. **AeroPulse FAQ & Methodology**

The central **Flight Choice Advisor** allows users to select:

- Origin airport
- Destination airport
- Month
- Preferred time window
- Traveler type: Business or Leisure

It then ranks the top three airline options and explains the recommendation.

### Core message

**AeroPulse doesn't just tell you which option to choose — it explains why.**

---

## Project Scope

The Flight Choice Advisor currently covers:

| Scope | Coverage |
|---|---:|
| Major German origin airports | 5 |
| Destination airports | 85 |
| Meaningful routes | 239 |
| Mapped airlines | 28 |
| Eligible flight records | 560K+ |
| OPDI observation period | Aug 2025 – Jul 2026 |

Origin airports:

- BER — Berlin
- FRA — Frankfurt
- DUS — Düsseldorf
- HAM — Hamburg
- MUC — Munich

---

## How AeroPulse Works

The analytical workflow can be summarized as:

**OBSERVE → ANALYZE → COMPARE → RECOMMEND**

### 1. Observe

Collect aviation observations and supporting reference data.

### 2. Analyze

Calculate route, airline, demand, growth, performance and seasonality indicators.

### 3. Compare

Compare airline and route alternatives within the selected scenario.

### 4. Recommend

Apply defined decision rules to produce explainable recommendations.

The recommendation layer is based on observed evidence and defined analytical rules. It is **not a predictive AI model**.

---

## AeroPulse Score

The core recommendation framework uses several analytical components, including:

- Demand
- Growth
- Performance
- Route strength
- Seasonality

These contribute to the broader **AeroPulse Score** and opportunity assessment.

Additional evidence layers such as price and passenger experience are intentionally kept separate from the core score.

This separation helps distinguish:

**core route/airline performance evidence**

from

**supporting decision evidence.**

---

## Evidence Layers

### Flight Timing Intelligence

Analyzes observed flight activity across detailed three-hour time windows.

The time windows are:

- 00:00–03:00 — Late Night
- 03:00–06:00 — Early Morning
- 06:00–09:00 — Morning
- 09:00–12:00 — Late Morning
- 12:00–15:00 — Midday
- 15:00–18:00 — Afternoon
- 18:00–21:00 — Evening
- 21:00–00:00 — Night

Important: these represent **observed activity periods derived from OPDI/ADS-B observations**, not scheduled departure times.

### Price & Market Intelligence

The price layer uses fare observations collected through Duffel test-mode data for selected routes and departure dates.

It provides:

- observed fare levels
- fare ranges
- route-relative price bands
- airline price positioning
- price evidence coverage

Price observations are **not presented as live market prices**.

The current production price dataset covers a limited set of routes and a departure date of **15 October 2026**.

### Passenger Experience Intelligence

Passenger experience analysis uses the **Airline Travel Reviews Data (Skytrax)** dataset.

The analysis covers:

- overall passenger rating
- seat comfort
- cabin staff service
- food & beverages
- inflight entertainment
- ground service
- Wi-Fi & connectivity
- value for money

Only airlines with verified name matches to the AeroPulse airline reference are included.

Passenger experience is presented as a separate evidence layer and is **not included in the core AeroPulse Performance/Opportunity Score**.

---

## Data Sources

### OpenSky / OPDI

The aviation activity layer is based on the **OpenSky Network Open Public Domain Air Traffic Data (OPDI)**.

The project uses observed flight activity from August 2025 through July 2026 for the main Flight Choice Advisor scope.

OPDI/ADS-B observations provide observed aircraft activity but do not directly provide commercial scheduled departure times in the basic dataset.

### Duffel

Duffel was used to collect test-mode fare observations for selected routes.

These observations are treated as fare snapshots rather than live market prices.

### Airline Travel Reviews Data (Skytrax)

Passenger-experience analysis uses:

**Airline Travel Reviews Data (Skytrax), 2015–2025**

Mendeley Data:

https://data.mendeley.com/datasets/vgjk58vf8h/1

DOI:

`10.17632/vgjk58vf8h.1`

The dataset contains passenger reviews and ratings across multiple airline-experience dimensions.

---

## Technology Stack

| Technology | Role |
|---|---|
| Python | Data processing, transformation and validation |
| SQL | Analytical modelling and recommendation logic |
| BigQuery | Data warehouse and analytical layer |
| Looker Studio | Interactive dashboard and visualization |
| Git / GitHub | Version control and portfolio documentation |

---

## Data Pipeline

The project follows a structured analytical pipeline:

```text
External Aviation Data
        ↓
Data Collection
        ↓
Python Transformation & Validation
        ↓
BigQuery
        ↓
Analytical Views & Recommendation Logic
        ↓
Looker Studio
        ↓
Interactive Decision Support