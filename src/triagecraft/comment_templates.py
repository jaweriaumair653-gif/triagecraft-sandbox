from __future__ import annotations

from triagecraft.models import DuplicateCandidate, LabelSuggestion, NormalizedIssue, Summary


def format_duplicate_comment(
    issue: NormalizedIssue,
    duplicates: list[DuplicateCandidate],
) -> str:
    if not duplicates:
        return ""

    top = duplicates[0]
    lines = [
        f"Possible duplicate detected for issue #{issue.issue_id}.",
        f"Closest match: issue #{top.issue_id} with confidence {top.confidence:.2f}.",
    ]

    if top.reason:
        lines.append(f"Reason: {top.reason}")

    return "\n".join(lines)


def format_label_comment(labels: list[LabelSuggestion]) -> str:
    if not labels:
        return ""

    parts = [f"`{item.label}` ({item.confidence:.2f})" for item in labels]
    return "Suggested labels: " + ", ".join(parts)


def format_info_request_comment(issue: NormalizedIssue) -> str:
    return (
        f"I need a bit more information on issue #{issue.issue_id}. "
        "Please include steps to reproduce, expected behavior, and any error logs."
    )


def format_summary_comment(summary: Summary) -> str:
    if not summary.text:
        return ""

    return f"Summary:\n{summary.text}"
