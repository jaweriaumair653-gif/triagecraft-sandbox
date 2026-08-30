# NYC 311 Operations Intelligence

An end-to-end public-data analytics system for municipal service operations.

This project turns NYC 311 service requests into an operational intelligence workflow covering resilient ingestion, data-quality checks, service-performance KPIs, spatial demand concentration, anomaly detection, and time-series forecasting.

## Core questions

- What demand is arriving, and how does it move over time?
- Which agencies and complaint types carry the largest workload and longest resolution tails?
- Which periods look operationally abnormal?
- Where does reported demand concentrate geographically?
- Does a forecasting model beat a simple 7-day seasonal-naive baseline?

## Architecture

```text
NYC Open Data / Socrata API
          |
          v
bounded paginated ingestion
          |
          v
raw NDJSON -> DuckDB/Parquet
          |
          v
canonical transformation + quality checks
          |
          +----> operational KPIs
          +----> spatial hotspots
          +----> robust anomaly detection
          +----> Isolation Forest
          +----> time-series forecast benchmark
          |
          v
reports / dashboard / decision support
```

## Technical scope

- Python, pandas, NumPy
- Socrata REST API with pagination and retry/backoff
- DuckDB + compressed Parquet
- SQL analytics
- data-quality validation
- feature engineering for temporal data
- robust rolling median/MAD anomaly detection
- Isolation Forest
- HistGradientBoostingRegressor
- seasonal-naive forecasting benchmark
- temporal holdout evaluation using MAE/RMSE/MAPE
- coarse geospatial demand grids
- Streamlit + Plotly dashboard entry point
- pytest coverage for transformations, KPIs, and forecasting

## Forecasting design

The forecasting module deliberately starts with a baseline: the request count from seven days earlier for the same weekday. A gradient-boosted model uses date features, lagged demand and shifted rolling means. The latest contiguous 28 days are held out for evaluation; random train/test shuffling is avoided to prevent temporal leakage.

## Anomaly design

Two independent signals are implemented: an interpretable robust rolling z-score using median absolute deviation, and Isolation Forest over demand/volatility features. Flags are prioritization signals, not causal conclusions.

## Data quality

The transformer defensively coerces dates and coordinates, handles optional API fields, deduplicates `unique_key`, detects impossible negative resolution durations, and exposes machine-readable quality diagnostics.

## Reproduce

```bash
python -m venv .venv
# Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev,dashboard]"
pytest
nyc311-intel download --start 2025-01-01 --end 2026-01-01 --out data/raw/nyc311.ndjson
nyc311-intel parquet --input data/raw/nyc311.ndjson --out data/curated/nyc311.parquet
python scripts/run_case_study.py --input data/curated/nyc311.parquet --output reports/latest
streamlit run src/nyc311_intelligence/dashboard.py
```

The repository intentionally does not vendor the full public dataset. The checked-in CSV is only a small smoke-test snapshot; population-level analysis should be reproduced from the official API for an explicit date range.

## Limitations

NYC 311 is reported service demand, not a census of all real-world problems. Resolution time can reflect workflow, scheduling, inspection, jurisdiction, verification, reopening and other operational factors. An anomaly is not automatically a root cause.

## Source

Official dataset: https://data.cityofnewyork.us/resource/erm2-nwe9.json

## Author

Jaweria Umair
