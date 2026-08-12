from __future__ import annotations

from datetime import datetime, timezone

from triagecraft.models import Issue, NormalizedIssue, RepositoryConfig
from triagecraft.service import TriageService


def test_process_issue_duplicate_branch() -> None:
    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        duplicate_threshold=0.2,
        label_threshold=0.75,
    )
    service = TriageService(config)

    issue = Issue(
        id=1,
        number=1,
        repository="owner/repo",
        title="Crash on login",
        body="App crashes when I sign in and cannot continue using the app",
        author="alice",
        labels=[],
        created_at=datetime.now(timezone.utc),
    )

    corpus = [
        NormalizedIssue(
            issue_id=2,
            clean_title="login crash",
            clean_body="application crashes during login and sign in",
            tokens=[
                "login",
                "crash",
                "application",
                "crashes",
                "during",
                "login",
                "sign",
                "in",
            ],
        )
    ]

    result = service.process_issue(issue, corpus)

    assert result.normalized_issue.issue_id == 1
    assert result.duplicate_candidates
    assert result.duplicate_candidates[0].issue_id == 2
    assert result.decision.should_comment is True
    assert result.decision.should_label is False
    assert result.decision.should_request_info is False
    assert result.decision.should_skip is False


def test_process_issue_label_branch() -> None:
    config = RepositoryConfig(
        repository="owner/repo",
        dry_run=False,
        label_threshold=0.1,
        duplicate_threshold=0.9,
    )
    service = TriageService(config)

    issue = Issue(
        id=3,
        number=3,
        repository="owner/repo",
        title="Bug: app crashes",
        body="The app throws an error and fails during login on every attempt",
        author="bob",
        labels=[],
        created_at=datetime.now(timezone.utc),
    )

    result = service.process_issue(issue, [])

    assert result.label_suggestions
    assert result.label_suggestions[0].label == "bug"
    assert result.decision.should_label is True
    assert result.decision.should_comment is True
    assert result.decision.should_request_info is False
    assert result.summary is not None
    assert result.summary.length > 0


def test_process_issue_dry_run_skips_actions() -> None:
    config = RepositoryConfig(repository="owner/repo", dry_run=True)
    service = TriageService(config)

    issue = Issue(
        id=4,
        number=4,
        repository="owner/repo",
        title="How do I install this?",
        body="Can you help me with setup?",
        author="carol",
        labels=[],
        created_at=datetime.now(timezone.utc),
    )

    result = service.process_issue(issue, [])

    assert result.decision.should_skip is True
    assert result.decision.should_comment is False
    assert result.decision.should_label is False
    assert result.decision.should_request_info is False
