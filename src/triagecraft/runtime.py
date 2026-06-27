from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from triagecraft.app import build_app, close_app
from triagecraft.server import create_server


@dataclass(slots=True)
class RuntimeSettings:
    config_path: Path
    db_path: Path
    github_token: str
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"


def load_runtime_settings(env: Mapping[str, str] | None = None) -> RuntimeSettings:
    """
    Load runtime settings from environment variables.
    """
    source = os.environ if env is None else env

    token = source.get("TRIAGECRAFT_GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing TRIAGECRAFT_GITHUB_TOKEN.")

    config_path = Path(source.get("TRIAGECRAFT_CONFIG_PATH", ".triagecraft.yml"))
    db_path = Path(source.get("TRIAGECRAFT_DB_PATH", "data/triagecraft.db"))

    host = source.get("TRIAGECRAFT_HOST", "127.0.0.1").strip() or "127.0.0.1"
    log_level = source.get("TRIAGECRAFT_LOG_LEVEL", "info").strip() or "info"

    port_raw = source.get("TRIAGECRAFT_PORT", "8000").strip()
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError("TRIAGECRAFT_PORT must be an integer.") from exc

    if port < 1 or port > 65535:
        raise RuntimeError("TRIAGECRAFT_PORT must be between 1 and 65535.")

    return RuntimeSettings(
        config_path=config_path,
        db_path=db_path,
        github_token=token,
        host=host,
        port=port,
        log_level=log_level,
    )


def run() -> None:
    """
    Build the app and start the webhook server.
    """
    load_dotenv()
    settings = load_runtime_settings()

    triage_app = build_app(
        settings.config_path,
        settings.github_token,
        settings.db_path,
    )
    server = create_server(triage_app)

    try:
        uvicorn.run(
            server,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level,
        )
    except KeyboardInterrupt:
        print("Stopping TriageCraft...")
    finally:
        close_app(triage_app)
