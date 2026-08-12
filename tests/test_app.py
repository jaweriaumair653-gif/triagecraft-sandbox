from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from triagecraft.action_engine import ActionEngine
from triagecraft.app import TriageApp, build_app, close_app, handle_webhook_payload
from triagecraft.models import NormalizedIssue, RepositoryConfig
from triagecraft.service import TriageService
from triagecraft.state_store import StateStore


@dataclass
class FakeClient:
    labels_calls: list[tuple[str, int, list[str]]]
    comments_calls: list[tuple[str, int, str]]
    closed: bool

    def __init__(self) -> None:
        self.labels_calls = []
        self.comments_calls = []
        self.closed = False

    def add_labels(self, repo_full_name: str, issue_number: int, labels: list[str]) -> list[str]:
        self.labels_calls.append((repo_full_name, issue_number, list(labels)))
        return list(labels)

    def post_comment(self, repo_full_name: str, issue_number: int, body: str) -> dict[str, Any]:
        self.comments_calls.append((repo_full_name, issue_number, body))
        return {"body": body}

    def close(self) -> None:
        self.closed = True


def test_build_app_uses_config_and_factory(tmp_path: Path) -> None:
    config_file = tmp_path / ".triagecraft.yml"
    config_file.write_text("repository: owner/repo\ndry_run: false\n", encoding="utf-8")

    fake_client = FakeClient()

    def factory(_: str) -> FakeClient:
        return fake_client

    app = build_app(
        config_file,
        token="secret",
        db_path=tmp_path / "state.db",
        client_factory=factory,
    )

    assert app.config.repository == "owner/repo"
    assert app.config.dry_run is False
    assert app.client is fake_client
    assert app.store is not None
    assert isinstance(app.service, TriageService)
    assert isinstance(app.engine, ActionEngine)


def test_handle_webhook_payload_runs_pipeline(tmp_path: Path) -> None:
    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        duplicate_threshold=0.2,
        label_threshold=0.1,
    )
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()
    service = TriageService(config)
    engine = ActionEngine(config=config, client=client, store=store)
    app = TriageApp(config=config, client=client, store=store, service=service, engine=engine)

    payload = {
        "event_type": "issues",
        "action": "opened",
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 1,
            "number": 1,
            "title": "Bug: app crashes",
            "body": "The app throws an error and fails during login on every attempt",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }

    corpus = [
        NormalizedIssue(
            issue_id=99,
            clean_title="bug app crashes",
            clean_body="the app throws an error and fails during login on every attempt",
            tokens=[
                "bug",
                "app",
                "crashes",
                "the",
                "app",
                "throws",
                "an",
                "error",
                "and",
                "fails",
                "during",
                "login",
                "on",
                "every",
                "attempt",
            ],
        )
    ]

    result = handle_webhook_payload(app, payload, event_id="evt-1", corpus=corpus)

    assert result.processed is True
    assert result.repository == "owner/repo"
    assert result.issue_id == 1
    assert result.duplicate_candidates >= 1
    assert "bug" in result.labels
    assert result.summary_length > 0
    assert result.labels_applied is True
    assert result.comment_posted is True
    assert client.labels_calls
    assert client.comments_calls
    assert store.has_processed_event("evt-1") is True
    assert result.duration_ms >= 0


def test_handle_webhook_payload_emits_logs(tmp_path: Path, caplog) -> None:
    caplog.set_level(logging.INFO, logger="triagecraft.app")

    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        duplicate_threshold=0.2,
        label_threshold=0.1,
    )
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()
    service = TriageService(config)
    engine = ActionEngine(config=config, client=client, store=store)
    app = TriageApp(config=config, client=client, store=store, service=service, engine=engine)

    payload = {
        "event_type": "issues",
        "action": "opened",
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 1,
            "number": 1,
            "title": "Bug: app crashes",
            "body": "The app throws an error and fails during login on every attempt",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }

    handle_webhook_payload(app, payload, event_id="evt-log", corpus=[])

    assert "Webhook received" in caplog.text
    assert "Processing complete" in caplog.text
    assert "Webhook execution complete" in caplog.text


def test_close_app_closes_client(tmp_path: Path) -> None:
    config = RepositoryConfig(repository="owner/repo", dry_run=True)
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()
    service = TriageService(config)
    engine = ActionEngine(config=config, client=client, store=store)
    app = TriageApp(config=config, client=client, store=store, service=service, engine=engine)

    close_app(app)

    assert client.closed is True
