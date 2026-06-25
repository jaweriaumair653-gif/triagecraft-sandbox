from __future__ import annotations

from triagecraft.models import NormalizedIssue, Summary


def summarize_issue(issue: NormalizedIssue, *, max_words: int = 30) -> Summary:
    """
    Create a short maintainer-friendly summary from a normalized issue.
    """
    parts: list[str] = []

    if issue.clean_title:
        parts.append(issue.clean_title)

    if issue.clean_body:
        parts.append(issue.clean_body)

    combined = " — ".join(parts).strip()
    if not combined:
        return Summary(text="", length=0)

    words = combined.split()
    if len(words) <= max_words:
        return Summary(text=combined, length=len(words))

    summary_text = " ".join(words[:max_words]).strip()
    return Summary(text=summary_text, length=max_words)
