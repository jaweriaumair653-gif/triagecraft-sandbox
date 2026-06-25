from __future__ import annotations

from triagecraft.duplicate_detector import (
    find_duplicate_candidates,
    jaccard_similarity,
    score_duplicate_pair,
)
from triagecraft.models import NormalizedIssue


def test_jaccard_similarity_basic() -> None:
    assert jaccard_similarity({"a", "b"}, {"b", "c"}) == 1 / 3
    assert jaccard_similarity(set(), {"b"}) == 0.0
    assert jaccard_similarity(set(), set()) == 0.0


def test_score_duplicate_pair_identical_issues() -> None:
    left = NormalizedIssue(
        issue_id=1,
        clean_title="app crashes on login",
        clean_body="steps app crashes on login",
        tokens=["app", "crashes", "on", "login", "steps", "app", "crashes", "on", "login"],
    )
    right = NormalizedIssue(
        issue_id=2,
        clean_title="app crashes on login",
        clean_body="steps app crashes on login",
        tokens=["app", "crashes", "on", "login", "steps", "app", "crashes", "on", "login"],
    )

    result = score_duplicate_pair(left, right)

    assert result.issue_id == 2
    assert result.confidence == 1.0
    assert "app" in result.reason


def test_find_duplicate_candidates_orders_best_match_first() -> None:
    target = NormalizedIssue(
        issue_id=1,
        clean_title="crash on login",
        clean_body="app crashes when logging in",
        tokens=["crash", "on", "login", "app", "crashes", "when", "logging", "in"],
    )
    close_match = NormalizedIssue(
        issue_id=2,
        clean_title="login crash",
        clean_body="application crashes during login",
        tokens=["login", "crash", "application", "crashes", "during", "login"],
    )
    weak_match = NormalizedIssue(
        issue_id=3,
        clean_title="documentation typo",
        clean_body="small text login issue",
        tokens=["documentation", "typo", "small", "text", "login", "issue"],
    )

    results = find_duplicate_candidates(target, [close_match, weak_match], top_n=2)

    assert len(results) == 2
    assert results[0].issue_id == 2
    assert results[0].confidence > results[1].confidence
    assert results[1].issue_id == 3
    assert results[1].confidence > 0


def test_find_duplicate_candidates_skips_self_and_ignores_zero_overlap() -> None:
    target = NormalizedIssue(
        issue_id=1,
        clean_title="crash on login",
        clean_body="app crashes when logging in",
        tokens=["crash", "on", "login"],
    )

    results = find_duplicate_candidates(target, [target], top_n=5)

    assert results == []
