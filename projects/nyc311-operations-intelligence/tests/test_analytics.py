import pandas as pd
from nyc311_intelligence.analytics import build_kpis, daily_demand, service_breakdown

def _frame():
    return pd.DataFrame({"unique_key":["1","2","3"],"created_day":pd.to_datetime(["2026-01-01","2026-01-01","2026-01-02"],utc=True),"is_closed":[True,False,True],"resolution_hours":[2.0,None,6.0],"agency":["A","A","B"],"complaint_type":["Noise","Noise","Water"],"borough":["X","X","Y"]})

def test_kpis_have_expected_values():
    k=build_kpis(_frame()); assert k["request_count"]==3; assert round(k["closed_rate_pct"],2)==66.67; assert k["median_resolution_hours"]==4.0

def test_daily_demand_and_breakdown():
    frame=_frame(); daily=daily_demand(frame); assert daily["requests"].tolist()==[2,1]; breakdown=service_breakdown(frame,"complaint_type",5); assert breakdown.iloc[0]["complaint_type"]=="Noise"
