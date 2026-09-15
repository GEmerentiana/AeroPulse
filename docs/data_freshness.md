# AeroPulse — Data Freshness Specification

## Objective

AeroPulse should maintain a rolling historical analysis rather than relying on a permanently fixed dataset.

## Required Metadata

The pipeline should track:

* latest_available_date
* earliest_available_date
* analysis_start_date
* analysis_end_date
* pipeline_refresh_date
* pipeline_refresh_timestamp

## Analysis Window

The preferred analytical window is the latest available 12 months.

Conceptually:

analysis_end_date = latest_available_date

analysis_start_date =
latest_available_date minus 12 months

## Refresh Process

A refresh should:

1. Connect to the source.
2. Determine the latest available data.
3. Identify records not already stored.
4. Download new records.
5. Validate the new records.
6. Remove duplicates.
7. Update the analytical dataset.
8. Recalculate derived metrics.
9. Refresh BigQuery tables.
10. Refresh the dashboard.

## Data Availability

The dashboard must not imply that data exists beyond the latest available source date.

## Transparency

The dashboard should display:

* Data available through
* Analysis period
* Last refreshed

## Real-Time Limitation

AeroPulse is not a real-time flight tracker.

The freshness of the dashboard depends on the underlying data source and its update frequency.
