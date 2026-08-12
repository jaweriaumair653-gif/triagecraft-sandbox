from __future__ import annotations

import logging
import time
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

logger = logging.getLogger(__name__)


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


@dataclass(slots=True)
class WebhookExecutionResult:
    processed: bool
    repository: str
    issue_id: int
    duplicate_candidates: int
    labels: list[str]
    should_comment: bool
    should_label: bool
    should_request_info: bool
    labels_applied: bool
    comment_posted: bool
    event_recorded: bool
    dry_run: bool
    summary_text: str
    summary_length: int
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "processed": self.processed,
            "repository": self.repository,
            "issue": self.issue_id,
            "duplicate_candidates": self.duplicate_candidates,
            "labels": self.labels,
            "should_comment": self.should_comment,
            "should_label": self.should_label,
            "should_request_info": self.should_request_info,
            "labels_applied": self.labels_applied,
            "comment_posted": self.comment_posted,
            "event_recorded": self.event_recorded,
            "dry_run": self.dry_run,
            "summary": {
                "text": self.summary_text,
                "length": self.summary_length,
            },
            "duration_ms": self.duration_ms,
        }


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
) -> WebhookExecutionResult:
    start_time = time.perf_counter()
    event = parse_webhook_event(payload)

    if event.issue is None:
        raise ValueError("Webhook payload does not contain an issue.")

    logger.info(
        "Webhook received repository=%s issue=%s action=%s",
        event.repository,
        event.issue.id,
        event.action,
    )

    result = app.service.process_issue(event.issue, list(corpus or []))
    labels = app.engine.select_labels(result)

    logger.info(
        "Processing complete repository=%s issue=%s duplicates=%s labels=%s",
        event.repository,
        event.issue.id,
        len(result.duplicate_candidates),
        labels,
    )

    action_result = app.engine.execute(
        repository=event.repository,
        issue_id=event.issue.number,
        result=result,
        event_id=event_id,
        event_created_at=event.issue.created_at.isoformat(),
    )


    summary_text = result.summary.text if result.summary is not None else ""
    summary_length = result.summary.length if result.summary is not None else 0
    duration_ms = (time.perf_counter() - start_time) * 1000

    execution = WebhookExecutionResult(
        processed=True,
        repository=event.repository,
        issue_id=event.issue.id,
        duplicate_candidates=len(result.duplicate_candidates),
        labels=labels,
        should_comment=result.decision.should_comment,
        should_label=result.decision.should_label,
        should_request_info=result.decision.should_request_info,
        labels_applied=action_result.labels_applied,
        comment_posted=action_result.comment_posted,
        event_recorded=action_result.event_recorded,
        dry_run=app.config.dry_run,
        summary_text=summary_text,
        summary_length=summary_length,
        duration_ms=duration_ms,
    )

    logger.info(
        "Webhook execution complete repository=%s issue=%s comment_posted=%s labels_applied=%s duration_ms=%.2f",
        event.repository,
        event.issue.id,
        execution.comment_posted,
        execution.labels_applied,
        execution.duration_ms,
    )

    return execution


def close_app(app: TriageApp) -> None:
    app.client.close()
