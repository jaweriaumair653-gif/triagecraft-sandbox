from __future__ import annotations

import pandas as pd


def build_kpis(df: pd.DataFrame) -> dict[str, float | int | None]:
    closed = df.loc[df["is_closed"] & df["resolution_hours"].notna(), "resolution_hours"]
    return {
        "request_count": int(len(df)),
        "closed_rate_pct": float(df["is_closed"].mean() * 100) if len(df) else None,
        "median_resolution_hours": float(closed.median()) if not closed.empty else None,
        "p90_resolution_hours": float(closed.quantile(0.90)) if not closed.empty else None,
        "late_over_72h_pct": float((closed > 72).mean() * 100) if not closed.empty else None,
        "unique_agencies": int(df["agency"].nunique(dropna=True)) if "agency" in df else 0,
        "unique_complaint_types": int(df["complaint_type"].nunique(dropna=True)) if "complaint_type" in df else 0,
    }


def daily_demand(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "requests"])
    return df.dropna(subset=["created_day"]).groupby("created_day", as_index=False).agg(requests=("unique_key", "size")).rename(columns={"created_day": "date"}).sort_values("date")


def service_breakdown(df: pd.DataFrame, by: str, top_n: int = 15) -> pd.DataFrame:
    if by not in df.columns:
        raise KeyError(f"Unknown breakdown dimension: {by}")
    result = df.groupby(by, dropna=False).agg(requests=("unique_key", "size"), closed_rate=("is_closed", "mean"), median_resolution_hours=("resolution_hours", "median"), p90_resolution_hours=("resolution_hours", lambda s: s.quantile(0.90))).reset_index().sort_values("requests", ascending=False).head(top_n)
    result["closed_rate_pct"] = result["closed_rate"] * 100
    return result.drop(columns=["closed_rate"])


def hotspot_table(df: pd.DataFrame, grid_precision: int = 2, min_requests: int = 10) -> pd.DataFrame:
    required = {"latitude", "longitude", "unique_key"}
    if not required.issubset(df.columns):
        raise KeyError(f"Missing columns: {sorted(required - set(df.columns))}")
    geo = df.dropna(subset=["latitude", "longitude"]).copy()
    if geo.empty:
        return pd.DataFrame(columns=["lat_cell", "lon_cell", "requests"])
    geo["lat_cell"] = geo["latitude"].round(grid_precision)
    geo["lon_cell"] = geo["longitude"].round(grid_precision)
    return geo.groupby(["lat_cell", "lon_cell"], as_index=False).agg(requests=("unique_key", "size")).query("requests >= @min_requests").sort_values("requests", ascending=False)
