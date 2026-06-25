from __future__ import annotations

from triagecraft.models import NormalizedIssue
from triagecraft.summarizer import summarize_issue


def test_summarize_issue_uses_title_and_body() -> None:
    issue = NormalizedIssue(
        issue_id=1,
        clean_title="app crash on login",
        clean_body="the app crashes every time i log in with my account",
        tokens=["app", "crash", "on", "login", "the", "app", "crashes"],
    )

    summary = summarize_issue(issue, max_words=10)

    assert summary.text
    assert summary.length == 10
    assert "app crash on login" in summary.text


def test_summarize_issue_handles_empty_text() -> None:
    issue = NormalizedIssue(
        issue_id=2,
        clean_title="",
        clean_body="",
        tokens=[],
    )

    summary = summarize_issue(issue)

    assert summary.text == ""
    assert summary.length == 0
