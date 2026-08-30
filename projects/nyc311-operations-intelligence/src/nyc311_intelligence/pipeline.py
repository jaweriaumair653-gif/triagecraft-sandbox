from __future__ import annotations
from pathlib import Path
import pandas as pd
from .transform import normalize_requests, validate_requests

def parquet_from_ndjson(ndjson_path: str | Path, parquet_path: str | Path) -> None:
    import duckdb
    ndjson = str(Path(ndjson_path).resolve()).replace("'", "''")
    parquet = Path(parquet_path)
    parquet.parent.mkdir(parents=True, exist_ok=True)
    out = str(parquet.resolve()).replace("'", "''")
    con = duckdb.connect()
    try:
        con.execute(f"COPY (SELECT * FROM read_json_auto('{ndjson}', format='newline_delimited')) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    finally:
        con.close()

def load_frame(path: str | Path, limit: int | None = None) -> pd.DataFrame:
    p = Path(path)
    if p.suffix == ".parquet":
        df = pd.read_parquet(p)
    elif p.suffix == ".csv":
        df = pd.read_csv(p)
    elif p.suffix in {".json", ".ndjson"}:
        df = pd.read_json(p, lines=(p.suffix == ".ndjson"))
    else:
        raise ValueError(f"Unsupported file type: {p.suffix}")
    return normalize_requests(df.head(limit) if limit else df)

def quality_report(path: str | Path) -> dict[str, object]:
    return validate_requests(load_frame(path))
