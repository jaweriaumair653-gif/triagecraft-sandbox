from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

@dataclass(frozen=True)
class ForecastResult:
    model_name: str
    horizon: int
    mae: float
    rmse: float
    mape_pct: float

def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.where(np.abs(y_true) < 1e-9, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100)

def _model() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(max_depth=6, learning_rate=0.06, max_iter=350, l2_regularization=1.0, random_state=42)

def make_daily_features(daily: pd.DataFrame, target: str = "requests") -> tuple[pd.DataFrame, pd.Series]:
    d = daily.sort_values("date").copy()
    d["dow"] = d["date"].dt.dayofweek
    d["month"] = d["date"].dt.month
    for lag in (1, 7, 14, 28):
        d[f"lag_{lag}"] = d[target].shift(lag)
    d["rolling_7"] = d[target].shift(1).rolling(7).mean()
    d["rolling_28"] = d[target].shift(1).rolling(28).mean()
    d = d.dropna().reset_index(drop=True)
    features = ["dow", "month", "lag_1", "lag_7", "lag_14", "lag_28", "rolling_7", "rolling_28"]
    return d[features], d[target]

def benchmark_forecaster(daily: pd.DataFrame, test_days: int = 28) -> list[ForecastResult]:
    d = daily.sort_values("date").copy()
    if len(d) < max(70, test_days + 35):
        raise ValueError("Need at least 70 daily observations for time-series benchmarking")
    X, y = make_daily_features(d)
    split = len(X) - test_days
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    model = _model().fit(X_train, y_train)
    pred = np.clip(model.predict(X_test), 0, None)
    baseline = d["requests"].shift(7).iloc[-test_days:].to_numpy()
    baseline = np.nan_to_num(baseline, nan=float(y_train.iloc[-7:].mean()))
    return [
        ForecastResult("seasonal_naive_7d", test_days, mean_absolute_error(y_test, baseline), mean_squared_error(y_test, baseline) ** 0.5, _mape(y_test.to_numpy(), baseline)),
        ForecastResult("hist_gradient_boosting", test_days, mean_absolute_error(y_test, pred), mean_squared_error(y_test, pred) ** 0.5, _mape(y_test.to_numpy(), pred)),
    ]
