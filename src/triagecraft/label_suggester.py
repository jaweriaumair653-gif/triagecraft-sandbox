from __future__ import annotations

from collections.abc import Iterable

from triagecraft.models import LabelSuggestion, NormalizedIssue

_LABEL_KEYWORDS: dict[str, set[str]] = {
    "bug": {
        "bug",
        "crash",
        "crashes",
        "error",
        "errors",
        "fail",
        "fails",
        "failed",
        "failure",
        "broken",
        "exception",
        "panic",
        "stacktrace",
        "stack",
    },
    "feature": {
        "feature",
        "enhancement",
        "request",
        "requests",
        "add",
        "adds",
        "adding",
        "support",
        "implement",
        "improve",
        "improvement",
    },
    "docs": {
        "docs",
        "doc",
        "documentation",
        "readme",
        "typo",
        "guide",
        "guides",
        "example",
        "examples",
        "spelling",
    },
    "question": {
        "question",
        "help",
        "how",
        "why",
        "what",
        "when",
        "where",
        "can",
        "could",
        "does",
        "do",
    },
    "needs-info": {
        "reproduce",
        "reproduction",
        "steps",
        "logs",
        "log",
        "version",
        "versions",
        "details",
        "information",
        "info",
        "screenshot",
    },
}


def _label_tokens(label: str) -> set[str]:
    normalized = label.strip().lower().replace("_", "-")
    parts = normalized.replace("-", " ").split()
    return {part for part in parts if part}


def _token_set(issue: NormalizedIssue) -> set[str]:
    return set(issue.tokens) | set(issue.clean_title.split()) | set(issue.clean_body.split())


def score_label(issue: NormalizedIssue, label: str) -> float:
    """
    Score how well a label matches an issue.

    The score is deterministic and based on keyword overlap only.
    """
    normalized_label = label.strip().lower()
    if not normalized_label:
        return 0.0

    issue_tokens = _token_set(issue)
    keyword_pool = set(_LABEL_KEYWORDS.get(normalized_label, set()))
    keyword_pool |= _label_tokens(normalized_label)

    if not keyword_pool:
        return 0.0

    hits = sum(1 for keyword in keyword_pool if keyword in issue_tokens)
    if hits == 0:
        return 0.0

    score = hits / len(keyword_pool)
    return round(min(score, 1.0), 4)


def suggest_labels(
    issue: NormalizedIssue,
    allowed_labels: Iterable[str],
    *,
    top_n: int | None = None,
) -> list[LabelSuggestion]:
    """
    Suggest labels for a normalized issue.

    Only labels in allowed_labels are considered.
    """
    suggestions: list[LabelSuggestion] = []

    for label in allowed_labels:
        confidence = score_label(issue, label)
        if confidence <= 0.0:
            continue
        suggestions.append(LabelSuggestion(label=label, confidence=confidence))

    suggestions.sort(key=lambda item: (-item.confidence, item.label))

    if top_n is not None:
        return suggestions[:top_n]

    return suggestions
