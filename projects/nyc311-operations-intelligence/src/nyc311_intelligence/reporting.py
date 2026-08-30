from __future__ import annotations
import json
from pathlib import Path
from .analytics import build_kpis, daily_demand, service_breakdown, hotspot_table
from .anomalies import isolation_forest_scores, robust_daily_anomalies
from .forecasting import benchmark_forecaster
from .pipeline import load_frame

def run_report(input_path: str | Path, output_dir: str | Path) -> dict[str, object]:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    df = load_frame(input_path); kpis = build_kpis(df); daily = daily_demand(df)
    (out / "kpis.json").write_text(json.dumps(kpis, indent=2, default=str), encoding="utf-8")
    service_breakdown(df, "agency", 25).to_csv(out / "agency_breakdown.csv", index=False)
    service_breakdown(df, "complaint_type", 25).to_csv(out / "complaint_breakdown.csv", index=False)
    hotspot_table(df, 2, max(2, len(df) // 500)).to_csv(out / "hotspots.csv", index=False)
    if len(daily) >= 70:
        robust_daily_anomalies(daily).to_csv(out / "robust_anomalies.csv", index=False)
        isolation_forest_scores(daily).to_csv(out / "iforest_scores.csv", index=False)
        (out / "forecast_benchmark.json").write_text(json.dumps([r.__dict__ for r in benchmark_forecaster(daily)], indent=2), encoding="utf-8")
    return kpis
