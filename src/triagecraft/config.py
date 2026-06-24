from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from triagecraft.models import RepositoryConfig

DEFAULT_CONFIG_NAME = ".triagecraft.yml"


def load_repository_config(path: str | Path) -> RepositoryConfig:
    """
    Load and validate a repository config file.

    The config file must be YAML and must match RepositoryConfig exactly.
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_text = config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw_text) or {}

    if not isinstance(data, dict):
        raise ValueError("Config file must contain a YAML mapping at the top level.")

    try:
        return RepositoryConfig.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid repository config: {exc}") from exc
