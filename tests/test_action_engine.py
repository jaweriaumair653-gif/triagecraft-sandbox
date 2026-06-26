from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from triagecraft.action_engine import ActionEngine
from triagecraft.models import (
    BotDecision,
    DuplicateCandidate,
    LabelSuggestion,
    NormalizedIssue,
    ProcessingResult,
    RepositoryConfig,
    Summary,
)
from triagecraft.state_store import StateStore


@dataclass
class FakeClient:
    labels_calls: list[tuple[str, int, list[str]]]
    comments_calls: list[tuple[str, int, str]]

    def __init__(self) -> None:
        self.labels_calls = []
        self.comments_calls = []

    def add_labels(self, repo_full_name: str, issue_number: int, labels: list[str]) -> list[str]:
        self.labels_calls.append((repo_full_name, issue_number, list(labels)))
        return list(labels)

    def post_comment(self, repo_full_name: str, issue_number: int, body: str) -> dict[str, Any]:
        self.comments_calls.append((repo_full_name, issue_number, body))
        return {"body": body}


def _build_result() -> ProcessingResult:
    normalized = NormalizedIssue(
        issue_id=1,
        clean_title="bug app crashes on login",
        clean_body="the app throws an error and fails during login",
        tokens=["bug", "app", "crashes", "on", "login", "error", "fails"],
    )

    return ProcessingResult(
        normalized_issue=normalized,
        duplicate_candidates=[
            DuplicateCandidate(
                issue_id=2,
                confidence=0.95,
                reason="Shared tokens: app, login, crash",
            )
        ],
        label_suggestions=[
            LabelSuggestion(label="bug", confidence=0.92),
            LabelSuggestion(label="docs", confidence=0.10),
        ],
        summary=Summary(text="App crashes during login", length=4),
        decision=BotDecision(
            should_comment=True,
            should_label=True,
            should_request_info=False,
            should_skip=False,
        ),
    )


def test_action_engine_applies_actions_once(tmp_path: Path) -> None:
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()

    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        duplicate_threshold=0.80,
        label_threshold=0.50,
    )
    engine = ActionEngine(config=config, client=client, store=store)

    result = _build_result()

    first = engine.execute(
        repository="owner/repo",
        issue_id=1,
        result=result,
        event_id="evt-1",
        event_created_at="2026-06-24T00:00:00Z",
    )

    assert first.labels_applied is True
    assert first.comment_posted is True
    assert first.event_recorded is True
    assert client.labels_calls == [("owner/repo", 1, ["bug"])]
    assert len(client.comments_calls) == 1
    assert "Summary:" in client.comments_calls[0][2]
    assert "Possible duplicate detected" in client.comments_calls[0][2]
    assert store.has_action("owner/repo", 1, "labels") is True
    assert store.has_action("owner/repo", 1, "comment") is True
    assert store.has_processed_event("evt-1") is True

    second = engine.execute(
        repository="owner/repo",
        issue_id=1,
        result=result,
        event_id="evt-1",
        event_created_at="2026-06-24T00:00:00Z",
    )

    assert second.labels_applied is False
    assert second.comment_posted is False
    assert len(client.labels_calls) == 1
    assert len(client.comments_calls) == 1


def test_action_engine_skips_dry_run(tmp_path: Path) -> None:
    store = StateStore(tmp_path / "state.db")
    client = FakeClient()

    config = RepositoryConfig(repository="owner/repo", dry_run=True)
    engine = ActionEngine(config=config, client=client, store=store)

    result = _build_result()

    outcome = engine.execute(
        repository="owner/repo",
        issue_id=1,
        result=result,
        event_id="evt-2",
        event_created_at="2026-06-24T00:00:00Z",
    )

    assert outcome.labels_applied is False
    assert outcome.comment_posted is False
    assert outcome.event_recorded is False
    assert client.labels_calls == []
    assert client.comments_calls == []
    assert store.has_processed_event("evt-2") is False
