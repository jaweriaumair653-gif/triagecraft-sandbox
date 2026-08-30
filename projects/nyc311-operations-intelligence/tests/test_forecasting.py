import numpy as np
import pandas as pd
from nyc311_intelligence.forecasting import benchmark_forecaster, make_daily_features

def test_features_are_lagged_and_have_expected_shape():
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    daily = pd.DataFrame({"date":dates,"requests":np.arange(60)+100})
    X, y = make_daily_features(daily)
    assert len(X) == len(y)
    assert {"lag_7","lag_28","rolling_7","rolling_28"}.issubset(X.columns)
    assert X.iloc[0]["lag_7"] < y.iloc[0]

def test_forecast_benchmark_returns_baseline_and_model():
    rng=np.random.default_rng(42); dates=pd.date_range("2025-01-01", periods=150, freq="D"); weekly=20*np.sin(2*np.pi*np.arange(150)/7)
    daily=pd.DataFrame({"date":dates,"requests":300+weekly+rng.normal(0,5,150)})
    results=benchmark_forecaster(daily, test_days=28)
    assert {r.model_name for r in results} == {"seasonal_naive_7d","hist_gradient_boosting"}
    assert all(r.mae >= 0 and r.rmse >= 0 for r in results)
