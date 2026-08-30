# NYC 311 Operations Intelligence

An end-to-end public-data analytics system for municipal service operations.

This project turns NYC 311 service requests into an operational intelligence workflow covering resilient ingestion, data-quality checks, service-performance KPIs, spatial demand concentration, anomaly detection, and time-series forecasting.

## Why it is portfolio-grade

This is intentionally not a four-line exploratory notebook. It demonstrates the full path from external data source to decision support:

```text
Socrata API -> paginated ingestion -> NDJSON -> DuckDB/Parquet
       -> canonical transformation -> data quality
       -> KPI / SQL analysis -> spatial + anomaly analysis
       -> leakage-aware forecast benchmark -> reports / dashboard
```

## Technical scope

- Python, pandas, NumPy
- Socrata REST API with pagination and retry/backoff
- DuckDB + compressed Parquet
- SQL analytics
- defensive data-quality validation
- temporal feature engineering
- robust rolling median/MAD anomaly detection
- Isolation Forest
- HistGradientBoostingRegressor
- seasonal-naive forecasting baseline
- MAE/RMSE/MAPE evaluation on a contiguous temporal holdout
- coarse geospatial demand grids
- pytest coverage
- optional Streamlit + Plotly dashboard

## Key analytical questions

1. What demand is arriving and how does it change over time?
2. Which agencies and complaint types carry the largest workload?
3. Which service categories have long resolution tails?
4. Which periods look operationally abnormal?
5. Where does reported demand concentrate?
6. Does a complex forecasting model beat a simple weekly seasonal baseline?

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

The full public dataset is intentionally not vendored. Use an explicit date window against the official API to reproduce population-level analysis.

## Forecasting design

The project compares a 7-day seasonal-naive baseline with gradient boosting using date features, 1/7/14/28-day lags and shifted rolling means. The latest contiguous 28 days are held out. Random shuffling is avoided because it can leak future information into a time-series problem.

## Anomaly design

Two independent detectors are provided: an interpretable robust rolling median/MAD score and Isolation Forest. Flags are prioritization signals, not causal explanations.

## Data-quality design

The transformation layer coerces dates and coordinates, handles optional fields, deduplicates `unique_key`, detects impossible negative resolution times, and exposes machine-readable diagnostics.

## Limitations

NYC 311 represents reported service demand, not a census of all real-world problems. Resolution time can reflect workflow, scheduling, inspection, jurisdiction, verification and reopening behavior. An anomaly does not establish a cause.

## Source

Official NYC Open Data 311 API: https://data.cityofnewyork.us/resource/erm2-nwe9.json

## Author

Jaweria Umair
