from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def robust_daily_anomalies(daily: pd.DataFrame, window: int = 28, threshold: float = 4.0) -> pd.DataFrame:
    d = daily.sort_values("date").copy()
    median = d["requests"].rolling(window, min_periods=max(7, window // 2)).median()
    mad = (d["requests"] - median).abs().rolling(window, min_periods=max(7, window // 2)).median()
    d["robust_z"] = 0.6745 * (d["requests"] - median) / mad.replace(0, np.nan)
    d["is_anomaly"] = d["robust_z"].abs() >= threshold
    d["anomaly_direction"] = np.where(d["robust_z"] > 0, "spike", "drop")
    return d

def isolation_forest_scores(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily.sort_values("date").copy()
    d["rolling_7"] = d["requests"].rolling(7, min_periods=7).mean()
    d["rolling_std_28"] = d["requests"].rolling(28, min_periods=14).std()
    features = d[["requests", "rolling_7", "rolling_std_28"]].fillna(0)
    if len(d) < 30:
        d["iforest_score"] = 0.0
        d["iforest_anomaly"] = False
        return d
    model = IsolationForest(n_estimators=300, contamination=0.02, random_state=42)
    labels = model.fit_predict(features)
    d["iforest_score"] = -model.score_samples(features)
    d["iforest_anomaly"] = labels == -1
    return d
