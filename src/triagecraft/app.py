from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from triagecraft.action_engine import ActionEngine, ActionResult
from triagecraft.config import load_repository_config
from triagecraft.github_client import GitHubClient
from triagecraft.models import NormalizedIssue, RepositoryConfig
from triagecraft.service import TriageService
from triagecraft.state_store import StateStore
from triagecraft.webhooks import parse_webhook_event


class RuntimeGitHubClient(Protocol):
    def add_labels(
        self, repo_full_name: str, issue_number: int, labels: Sequence[str]
    ) -> list[str]: ...

    def post_comment(self, repo_full_name: str, issue_number: int, body: str) -> dict[str, Any]: ...

    def close(self) -> None: ...


ClientFactory = Callable[[str], RuntimeGitHubClient]


@dataclass(slots=True)
class TriageApp:
    config: RepositoryConfig
    client: RuntimeGitHubClient
    store: StateStore
    service: TriageService
    engine: ActionEngine


def build_app(
    config_path: str | Path,
    token: str,
    db_path: str | Path,
    *,
    client_factory: ClientFactory = GitHubClient,
) -> TriageApp:
    config = load_repository_config(config_path)
    store = StateStore(Path(db_path))
    client = client_factory(token)
    service = TriageService(config)
    engine = ActionEngine(config=config, client=client, store=store)

    return TriageApp(
        config=config,
        client=client,
        store=store,
        service=service,
        engine=engine,
    )


def handle_webhook_payload(
    app: TriageApp,
    payload: dict[str, Any],
    *,
    event_id: str | None = None,
    corpus: Sequence[NormalizedIssue] | None = None,
) -> ActionResult:
    event = parse_webhook_event(payload)

    if event.issue is None:
        raise ValueError("Webhook payload does not contain an issue.")

    result = app.service.process_issue(event.issue, list(corpus or []))

    return app.engine.execute(
        repository=event.repository,
        issue_id=event.issue.id,
        result=result,
        event_id=event_id,
        event_created_at=event.issue.created_at.isoformat(),
    )


def close_app(app: TriageApp) -> None:
    app.client.close()
