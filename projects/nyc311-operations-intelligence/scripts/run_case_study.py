from __future__ import annotations
import argparse
from pathlib import Path
from nyc311_intelligence.reporting import run_report

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--input", required=True); p.add_argument("--output", default="reports/latest"); args=p.parse_args()
    kpis = run_report(Path(args.input), Path(args.output))
    print("Report complete")
    for key, value in kpis.items(): print(f"{key}: {value}")

if __name__ == "__main__": main()
