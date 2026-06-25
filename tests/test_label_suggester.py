from __future__ import annotations

from triagecraft.label_suggester import score_label, suggest_labels
from triagecraft.models import NormalizedIssue


def test_bug_issue_prefers_bug_label() -> None:
    issue = NormalizedIssue(
        issue_id=1,
        clean_title="app crash on login",
        clean_body="the app throws an error and fails",
        tokens=[
            "app",
            "crash",
            "on",
            "login",
            "the",
            "app",
            "throws",
            "an",
            "error",
            "and",
            "fails",
        ],
    )

    suggestions = suggest_labels(issue, ["bug", "feature", "docs", "question"])

    assert suggestions
    assert suggestions[0].label == "bug"
    assert suggestions[0].confidence > 0
    assert all(suggestions[0].confidence >= item.confidence for item in suggestions[1:])


def test_docs_issue_prefers_docs_label() -> None:
    issue = NormalizedIssue(
        issue_id=2,
        clean_title="readme typo",
        clean_body="documentation example is unclear",
        tokens=["readme", "typo", "documentation", "example", "is", "unclear"],
    )

    suggestions = suggest_labels(issue, ["bug", "feature", "docs", "question"])

    assert suggestions
    assert suggestions[0].label == "docs"
    assert suggestions[0].confidence > 0


def test_question_issue_prefers_question_label() -> None:
    issue = NormalizedIssue(
        issue_id=3,
        clean_title="how do I install this",
        clean_body="can you help with setup",
        tokens=["how", "do", "i", "install", "this", "can", "you", "help", "with", "setup"],
    )

    suggestions = suggest_labels(issue, ["bug", "feature", "docs", "question"])

    assert suggestions
    assert suggestions[0].label == "question"
    assert suggestions[0].confidence > 0


def test_unknown_labels_are_ignored() -> None:
    issue = NormalizedIssue(
        issue_id=4,
        clean_title="crash on startup",
        clean_body="error on launch",
        tokens=["crash", "on", "startup", "error", "on", "launch"],
    )

    suggestions = suggest_labels(issue, ["security", "ops"])

    assert suggestions == []


def test_score_label_is_deterministic() -> None:
    issue = NormalizedIssue(
        issue_id=5,
        clean_title="feature request for dark mode",
        clean_body="please add support",
        tokens=["feature", "request", "for", "dark", "mode", "please", "add", "support"],
    )

    first = score_label(issue, "feature")
    second = score_label(issue, "feature")

    assert first == second
    assert 0.0 <= first <= 1.0
