from __future__ import annotations

from triagecraft.comment_templates import (
    format_duplicate_comment,
    format_info_request_comment,
    format_label_comment,
    format_summary_comment,
)
from triagecraft.models import DuplicateCandidate, LabelSuggestion, NormalizedIssue, Summary


def test_format_duplicate_comment() -> None:
    issue = NormalizedIssue(
        issue_id=1,
        clean_title="crash on login",
        clean_body="app crashes on login",
        tokens=["crash", "login"],
    )
    duplicates = [
        DuplicateCandidate(issue_id=2, confidence=0.91, reason="Shared tokens: crash, login")
    ]

    text = format_duplicate_comment(issue, duplicates)

    assert "issue #1" in text
    assert "issue #2" in text
    assert "0.91" in text


def test_format_label_comment() -> None:
    labels = [
        LabelSuggestion(label="bug", confidence=0.88),
        LabelSuggestion(label="docs", confidence=0.41),
    ]

    text = format_label_comment(labels)

    assert "`bug`" in text
    assert "`docs`" in text


def test_format_info_request_comment() -> None:
    issue = NormalizedIssue(
        issue_id=5,
        clean_title="help",
        clean_body="",
        tokens=["help"],
    )

    text = format_info_request_comment(issue)

    assert "issue #5" in text
    assert "steps to reproduce" in text


def test_format_summary_comment() -> None:
    summary = Summary(text="App crashes during login", length=4)

    text = format_summary_comment(summary)

    assert "Summary:" in text
    assert "App crashes during login" in text
