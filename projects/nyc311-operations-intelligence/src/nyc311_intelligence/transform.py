from __future__ import annotations

import numpy as np
import pandas as pd

DATE_COLUMNS = ["created_date", "closed_date"]
CATEGORICAL_COLUMNS = ["agency", "agency_name", "complaint_type", "descriptor", "borough", "status", "open_data_channel_type"]


def normalize_requests(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    for col in DATE_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
        else:
            out[col] = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    for col in ["latitude", "longitude"]:
        out[col] = pd.to_numeric(out[col], errors="coerce") if col in out else np.nan
    out.loc[~out["latitude"].between(-90, 90), "latitude"] = np.nan
    out.loc[~out["longitude"].between(-180, 180), "longitude"] = np.nan
    for col in ["incident_zip", "community_board", "council_district", "police_precinct"]:
        if col in out.columns:
            out[col] = out[col].astype("string").str.strip()
    for col in CATEGORICAL_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype("string").str.strip()
    if "unique_key" in out.columns:
        out["unique_key"] = out["unique_key"].astype("string").str.strip()
        out = out.drop_duplicates(subset=["unique_key"], keep="last").reset_index(drop=True)
    out["is_closed"] = out["closed_date"].notna()
    out["resolution_hours"] = (out["closed_date"] - out["created_date"]).dt.total_seconds() / 3600
    out.loc[out["resolution_hours"] < 0, "resolution_hours"] = np.nan
    out["created_day"] = out["created_date"].dt.floor("D")
    out["created_date_local"] = out["created_date"].dt.tz_convert("America/New_York")
    out["day_of_week"] = out["created_date_local"].dt.day_name()
    out["hour"] = out["created_date_local"].dt.hour
    out["month"] = out["created_date_local"].dt.month
    out["year"] = out["created_date_local"].dt.year
    out["week_of_year"] = out["created_date_local"].dt.isocalendar().week.astype("Int64")
    out["is_weekend"] = out["created_date_local"].dt.dayofweek >= 5
    return out


def validate_requests(df: pd.DataFrame) -> dict[str, object]:
    return {
        "row_count": int(len(df)),
        "unique_key_present": "unique_key" in df.columns,
        "duplicate_keys": int(df["unique_key"].duplicated().sum()) if "unique_key" in df.columns else None,
        "missing_created_date_pct": float(df["created_date"].isna().mean()) if "created_date" in df.columns else 1.0,
        "invalid_resolution_count": int((df["resolution_hours"] < 0).sum()) if "resolution_hours" in df.columns else None,
        "coordinate_valid_pct": float((df["latitude"].notna() & df["longitude"].notna()).mean()) if {"latitude", "longitude"}.issubset(df.columns) else 0.0,
    }
