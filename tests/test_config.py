from pathlib import Path

import pytest

from triagecraft.config import load_repository_config


def test_load_repository_config_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / ".triagecraft.yml"
    config_file.write_text("repository: owner/repo\n", encoding="utf-8")

    config = load_repository_config(config_file)

    assert config.repository == "owner/repo"
    assert config.dry_run is True
    assert "bug" in config.allowed_labels


def test_load_repository_config_custom_values(tmp_path: Path) -> None:
    config_file = tmp_path / ".triagecraft.yml"
    config_file.write_text(
        """
repository: owner/repo
duplicate_threshold: 0.9
label_threshold: 0.8
summary_threshold: 0.7
dry_run: false
allowed_labels:
  - bug
  - docs
""".strip(),
        encoding="utf-8",
    )

    config = load_repository_config(config_file)

    assert config.duplicate_threshold == 0.9
    assert config.label_threshold == 0.8
    assert config.summary_threshold == 0.7
    assert config.dry_run is False
    assert config.allowed_labels == ["bug", "docs"]


def test_load_repository_config_missing_file_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "missing.yml"

    with pytest.raises(FileNotFoundError):
        load_repository_config(config_file)


def test_load_repository_config_rejects_invalid_yaml_structure(tmp_path: Path) -> None:
    config_file = tmp_path / ".triagecraft.yml"
    config_file.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_repository_config(config_file)
