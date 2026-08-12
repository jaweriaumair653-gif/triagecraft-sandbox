from __future__ import annotations

from datetime import datetime, timezone

from triagecraft.models import Issue
from triagecraft.normalizer import normalize_issue, normalize_text, tokenize_text


def test_normalize_text_removes_urls_and_punctuation() -> None:
    text = "Crash here: https://example.com/docs!!!"
    assert normalize_text(text) == "crash here"


def test_normalize_text_collapses_whitespace() -> None:
    text = "  Hello   WORLD \n\t  "
    assert normalize_text(text) == "hello world"


def test_tokenize_text_returns_clean_tokens() -> None:
    text = "Bug report for v2.0"
    assert tokenize_text(text) == ["bug", "report", "for", "v2", "0"]


def test_normalize_issue_builds_structured_result() -> None:
    issue = Issue(
        id=10,
        number=10,
        repository="owner/repo",
        title="Crash on login!!!",
        body="Steps: open app, visit https://example.com, then crash.",
        author="alice",
        labels=["bug"],
        created_at=datetime.now(timezone.utc),
    )

    normalized = normalize_issue(issue)

    assert normalized.issue_id == 10
    assert normalized.clean_title == "crash on login"
    assert normalized.clean_body == "steps open app visit then crash"
    assert "crash" in normalized.tokens
    assert "login" in normalized.tokens
    assert "https" not in normalized.tokens
