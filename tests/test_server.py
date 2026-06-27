from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from triagecraft.action_engine import ActionEngine
from triagecraft.app import TriageApp
from triagecraft.models import RepositoryConfig
from triagecraft.server import create_server
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


def _build_triage_app(tmp_path: Path, secret: str = "topsecret") -> TriageApp:
    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        duplicate_threshold=0.2,
        label_threshold=0.1,
        webhook_secret=secret,
    )
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()
    service = TriageService(config)
    engine = ActionEngine(config=config, client=client, store=store)
    return TriageApp(config=config, client=client, store=store, service=service, engine=engine)


def _signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_health_endpoint_returns_ok(tmp_path: Path) -> None:
    triage_app = _build_triage_app(tmp_path)
    server = create_server(triage_app)
    client = TestClient(server)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_endpoint_processes_issue_event(tmp_path: Path) -> None:
    triage_app = _build_triage_app(tmp_path, secret="supersecret")
    server = create_server(triage_app)
    client = TestClient(server)

    payload = {
        "action": "opened",
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 1,
            "title": "Bug: app crashes",
            "body": "The app throws an error and fails during login on every attempt",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Delivery": "evt-1",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": _signature("supersecret", body),
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["event"] == "issues"
    assert response.json()["delivery_id"] == "evt-1"
    assert response.json()["labels_applied"] is True
    assert response.json()["comment_posted"] is True


def test_webhook_endpoint_rejects_bad_signature(tmp_path: Path) -> None:
    triage_app = _build_triage_app(tmp_path, secret="supersecret")
    server = create_server(triage_app)
    client = TestClient(server)

    payload = {
        "action": "opened",
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 1,
            "title": "Bug: app crashes",
            "body": "The app throws an error and fails during login on every attempt",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Delivery": "evt-2",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": "sha256=bad",
        },
    )

    assert response.status_code == 401
