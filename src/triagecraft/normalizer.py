from __future__ import annotations

import re

from triagecraft.models import Issue, NormalizedIssue

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_NON_WORD_RE = re.compile(r"[^a-z0-9\s]+")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str | None) -> str:
    """
    Convert free-form text into a consistent lowercase, URL-free, whitespace-normalized string.
    """
    if value is None:
        return ""

    text = value.lower().strip()
    text = _URL_RE.sub(" ", text)
    text = _NON_WORD_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def tokenize_text(value: str | None) -> list[str]:
    """
    Turn normalized text into tokens.
    """
    normalized = normalize_text(value)
    if not normalized:
        return []
    return normalized.split(" ")


def normalize_issue(issue: Issue) -> NormalizedIssue:
    """
    Normalize issue title and body into a structured representation.
    """
    clean_title = normalize_text(issue.title)
    clean_body = normalize_text(issue.body)

    tokens = tokenize_text(issue.title)
    tokens.extend(tokenize_text(issue.body))

    return NormalizedIssue(
        issue_id=issue.id,
        clean_title=clean_title,
        clean_body=clean_body,
        tokens=tokens,
    )
