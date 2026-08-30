import pandas as pd
from nyc311_intelligence.transform import normalize_requests, validate_requests

def test_normalize_creates_temporal_and_resolution_features():
    raw = pd.DataFrame([{"unique_key":"1","created_date":"2026-01-01T08:00:00Z","closed_date":"2026-01-02T08:00:00Z","latitude":40.7,"longitude":-73.9},{"unique_key":"1","created_date":"2026-01-01T08:00:00Z","closed_date":"2026-01-02T08:00:00Z","latitude":40.7,"longitude":-73.9}])
    out = normalize_requests(raw)
    assert len(out) == 1
    assert out.iloc[0]["resolution_hours"] == 24
    assert bool(out.iloc[0]["is_closed"])
    assert "day_of_week" in out.columns

def test_quality_report_detects_invalid_coordinates_and_missing_created_date():
    out = normalize_requests(pd.DataFrame([{"unique_key":"1","created_date":None,"latitude":999,"longitude":-999}]))
    qa = validate_requests(out)
    assert qa["missing_created_date_pct"] == 1.0
    assert qa["coordinate_valid_pct"] == 0.0
