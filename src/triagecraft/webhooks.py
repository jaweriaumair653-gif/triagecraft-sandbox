from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from triagecraft.models import Issue, WebhookEvent


class WebhookParseError(ValueError):
    """Raised when a GitHub webhook payload cannot be parsed safely."""


def _get_required_str(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WebhookParseError(f"Missing or invalid {key!r} in {context}.")
    return value.strip()


def _get_required_int(data: dict[str, Any], key: str, context: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise WebhookParseError(f"Missing or invalid {key!r} in {context}.")
    return value


def _get_optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise WebhookParseError(f"Invalid {key!r}; expected string or null.")
    stripped = value.strip()
    return stripped if stripped else None


def _parse_datetime(value: str, context: str) -> datetime:
    """
    Parse an ISO-8601 datetime string safely.

    GitHub webhook timestamps commonly end in 'Z', which we convert to UTC.
    """
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise WebhookParseError(f"Invalid datetime in {context}: {value!r}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def parse_issue_from_payload(payload: dict[str, Any]) -> Issue:
    """
    Extract and validate an Issue object from a GitHub issue webhook payload.
    """
    repository = payload.get("repository")
    issue_data = payload.get("issue")

    if not isinstance(repository, dict):
        raise WebhookParseError("Missing or invalid repository object.")
    if not isinstance(issue_data, dict):
        raise WebhookParseError("Missing or invalid issue object.")

    repo_full_name = _get_required_str(repository, "full_name", "repository")
    issue_id = _get_required_int(issue_data, "id", "issue")
    title = _get_required_str(issue_data, "title", "issue")

    author_data = issue_data.get("user")
    if not isinstance(author_data, dict):
        raise WebhookParseError("Missing or invalid issue.user object.")
    author = _get_required_str(author_data, "login", "issue.user")

    labels_raw = issue_data.get("labels", [])
    labels: list[str] = []
    if labels_raw is None:
        labels_raw = []
    if not isinstance(labels_raw, list):
        raise WebhookParseError("Invalid issue.labels; expected a list.")

    for label in labels_raw:
        if not isinstance(label, dict):
            raise WebhookParseError("Invalid label entry in issue.labels.")
        name = _get_required_str(label, "name", "issue.labels")
        labels.append(name)

    body = _get_optional_str(issue_data, "body")
    created_at_raw = _get_required_str(issue_data, "created_at", "issue")
    created_at = _parse_datetime(created_at_raw, "issue.created_at")

    return Issue(
        id=issue_id,
        repository=repo_full_name,
        title=title,
        body=body,
        author=author,
        labels=labels,
        created_at=created_at,
    )


def parse_webhook_event(payload: dict[str, Any]) -> WebhookEvent:
    """
    Convert a raw GitHub webhook payload into a typed WebhookEvent.
    """
    if not isinstance(payload, dict):
        raise WebhookParseError("Payload must be a JSON object.")

    event_type = _get_required_str(payload, "event_type", "payload")
    action = _get_required_str(payload, "action", "payload")
    repository_obj = payload.get("repository")

    if not isinstance(repository_obj, dict):
        raise WebhookParseError("Missing or invalid repository object.")

    repository = _get_required_str(repository_obj, "full_name", "repository")

    issue: Issue | None = None
    if "issue" in payload:
        issue = parse_issue_from_payload(payload)

    return WebhookEvent(
        event_type=event_type,
        action=action,
        repository=repository,
        issue=issue,
        payload=payload,
    )
