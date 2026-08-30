from __future__ import annotations
import argparse, json
from .ingest import download_ndjson
from .pipeline import parquet_from_ndjson, quality_report

def main() -> None:
    parser = argparse.ArgumentParser(prog="nyc311-intel")
    sub = parser.add_subparsers(dest="command", required=True)
    dl = sub.add_parser("download"); dl.add_argument("--start", required=True); dl.add_argument("--end", required=True); dl.add_argument("--out", default="data/raw/nyc311.ndjson"); dl.add_argument("--page-size", type=int, default=50_000)
    pq = sub.add_parser("parquet"); pq.add_argument("--input", required=True); pq.add_argument("--out", default="data/curated/nyc311.parquet")
    qa = sub.add_parser("quality"); qa.add_argument("--input", required=True)
    args = parser.parse_args()
    if args.command == "download": print(json.dumps({"rows_downloaded": download_ndjson(args.start, args.end, args.out, args.page_size), "output": args.out}, indent=2))
    elif args.command == "parquet": parquet_from_ndjson(args.input, args.out); print(json.dumps({"parquet": args.out}, indent=2))
    elif args.command == "quality": print(json.dumps(quality_report(args.input), indent=2, default=str))

if __name__ == "__main__": main()
