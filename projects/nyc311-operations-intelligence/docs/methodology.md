# Methodology

## Leakage prevention
Forecast features are based only on information available before the prediction date. Lagged values and rolling statistics are shifted by one day. Evaluation uses the latest contiguous test window rather than random shuffling.

## Baseline-first modeling
A 7-day seasonal-naive forecast is the benchmark. A more complex model is only useful if it improves held-out MAE/RMSE/MAPE.

## Anomalies
Demand anomalies use a robust rolling median/MAD score plus Isolation Forest. Flags are investigation priorities, not proof of unusual causes.

## Spatial analysis
Coordinates are rounded into coarse cells before aggregation so the analysis focuses on demand concentration rather than individual locations.

## Limitations
311 is reported demand rather than an unbiased census. Resolution time reflects operational workflow as well as underlying conditions.
