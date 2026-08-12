from __future__ import annotations

import pytest

from triagecraft.webhooks import WebhookParseError, parse_issue_from_payload, parse_webhook_event


def test_parse_issue_from_payload() -> None:
    payload = {
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 123,
            "number": 15,
            "title": "Bug: app crashes",
            "body": "Steps to reproduce...",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}, {"name": "help wanted"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }

    issue = parse_issue_from_payload(payload)

    assert issue.id == 123
    assert issue.number == 15
    assert issue.repository == "owner/repo"
    assert issue.title == "Bug: app crashes"
    assert issue.body == "Steps to reproduce..."
    assert issue.author == "alice"
    assert issue.labels == ["bug", "help wanted"]


def test_parse_webhook_event_with_issue() -> None:
    payload = {
        "event_type": "issues",
        "action": "opened",
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 123,
            "number": 15,
            "title": "Bug: app crashes",
            "body": "Steps to reproduce...",
            "user": {"login": "alice"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-06-24T10:00:00Z",
        },
    }

    event = parse_webhook_event(payload)

    assert event.event_type == "issues"
    assert event.action == "opened"
    assert event.repository == "owner/repo"
    assert event.issue is not None
    assert event.issue.id == 123
    assert event.issue.number == 15


def test_parse_webhook_event_rejects_missing_repository() -> None:
    payload = {"event_type": "issues", "action": "opened"}

    with pytest.raises(WebhookParseError):
        parse_webhook_event(payload)


def test_parse_issue_from_payload_rejects_bad_labels() -> None:
    payload = {
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 123,
            "number": 16,
            "title": "Bug",
            "body": None,
            "user": {"login": "alice"},
            "labels": "bug",
            "created_at": "2026-06-24T10:00:00Z",
        },
    }

    with pytest.raises(WebhookParseError):
        parse_issue_from_payload(payload)


def test_parse_issue_from_payload_rejects_bad_datetime() -> None:
    payload = {
        "repository": {"full_name": "owner/repo"},
        "issue": {
            "id": 123,
            "number": 16,
            "title": "Bug",
            "body": None,
            "user": {"login": "alice"},
            "labels": [],
            "created_at": "not-a-datetime",
        },
    }

    with pytest.raises(WebhookParseError):
        parse_issue_from_payload(payload)
