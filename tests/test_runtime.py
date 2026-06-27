from __future__ import annotations

from pathlib import Path

import pytest

from triagecraft.runtime import load_runtime_settings, run


def test_load_runtime_settings_defaults() -> None:
    env = {"TRIAGECRAFT_GITHUB_TOKEN": "secret"}
    settings = load_runtime_settings(env)

    assert settings.config_path == Path(".triagecraft.yml")
    assert settings.db_path == Path("data/triagecraft.db")
    assert settings.github_token == "secret"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.log_level == "info"


def test_load_runtime_settings_custom_values() -> None:
    env = {
        "TRIAGECRAFT_GITHUB_TOKEN": "secret",
        "TRIAGECRAFT_CONFIG_PATH": "config/custom.yml",
        "TRIAGECRAFT_DB_PATH": "var/state.db",
        "TRIAGECRAFT_HOST": "0.0.0.0",
        "TRIAGECRAFT_PORT": "9000",
        "TRIAGECRAFT_LOG_LEVEL": "debug",
    }
    settings = load_runtime_settings(env)

    assert settings.config_path == Path("config/custom.yml")
    assert settings.db_path == Path("var/state.db")
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.log_level == "debug"


def test_load_runtime_settings_rejects_missing_token() -> None:
    with pytest.raises(RuntimeError):
        load_runtime_settings({})


def test_load_runtime_settings_rejects_bad_port() -> None:
    env = {
        "TRIAGECRAFT_GITHUB_TOKEN": "secret",
        "TRIAGECRAFT_PORT": "not-a-number",
    }

    with pytest.raises(RuntimeError):
        load_runtime_settings(env)


def test_run_wires_all_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    fake_app = object()
    fake_server = object()

    def fake_build_app(config_path, token, db_path):
        calls["build_app"] = (config_path, token, db_path)
        return fake_app

    def fake_create_server(app):
        calls["create_server"] = app
        return fake_server

    def fake_uvicorn_run(app, host, port, log_level):
        calls["uvicorn_run"] = (app, host, port, log_level)

    def fake_close_app(app):
        calls["close_app"] = app

    monkeypatch.setenv("TRIAGECRAFT_GITHUB_TOKEN", "secret")
    monkeypatch.setenv("TRIAGECRAFT_HOST", "127.0.0.1")
    monkeypatch.setenv("TRIAGECRAFT_PORT", "8000")
    monkeypatch.setattr("triagecraft.runtime.load_dotenv", lambda: None)
    monkeypatch.setattr("triagecraft.runtime.build_app", fake_build_app)
    monkeypatch.setattr("triagecraft.runtime.create_server", fake_create_server)
    monkeypatch.setattr("triagecraft.runtime.uvicorn.run", fake_uvicorn_run)
    monkeypatch.setattr("triagecraft.runtime.close_app", fake_close_app)

    run()

    assert calls["build_app"] == (
        Path(".triagecraft.yml"),
        "secret",
        Path("data/triagecraft.db"),
    )
    assert calls["create_server"] is fake_app
    assert calls["uvicorn_run"] == (fake_server, "127.0.0.1", 8000, "info")
    assert calls["close_app"] is fake_app
