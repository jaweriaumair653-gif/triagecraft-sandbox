from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
DEFAULT_PAGE_SIZE = 50_000


def _session() -> requests.Session:
    retry = Retry(total=5, connect=5, read=5, status=5, backoff_factor=1.5, status_forcelist=(429,500,502,503,504), allowed_methods=frozenset({"GET"}), respect_retry_after_header=True)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    token = os.getenv("NYC311_APP_TOKEN")
    if token:
        session.headers.update({"X-App-Token": token})
    return session


def fetch_pages(start_date: str, end_date: str, page_size: int = DEFAULT_PAGE_SIZE) -> Iterator[list[dict]]:
    if start_date >= end_date:
        raise ValueError("start_date must be earlier than end_date")
    offset = 0
    session = _session()
    where = f"created_date >= '{start_date}T00:00:00' AND created_date < '{end_date}T00:00:00'"
    while True:
        response = session.get(API_URL, params={"$limit": page_size, "$offset": offset, "$order": "created_date ASC", "$where": where}, timeout=90)
        response.raise_for_status()
        page = response.json()
        if not page:
            break
        yield page
        offset += len(page)
        if len(page) < page_size:
            break


def download_ndjson(start_date: str, end_date: str, out_path: str | Path, page_size: int = DEFAULT_PAGE_SIZE) -> int:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open("w", encoding="utf-8") as handle:
        for page in fetch_pages(start_date, end_date, page_size):
            for row in page:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
                count += 1
    return count
