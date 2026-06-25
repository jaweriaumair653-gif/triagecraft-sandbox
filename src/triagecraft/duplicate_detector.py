from __future__ import annotations

from triagecraft.models import DuplicateCandidate, NormalizedIssue


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    """
    Compute Jaccard similarity between two token sets.
    """
    if not left or not right:
        return 0.0

    intersection = len(left & right)
    union = len(left | right)
    if union == 0:
        return 0.0

    return intersection / union


def _token_set(issue: NormalizedIssue) -> set[str]:
    return set(issue.tokens)


def score_duplicate_pair(target: NormalizedIssue, candidate: NormalizedIssue) -> DuplicateCandidate:
    """
    Score how likely candidate is a duplicate of target.
    """
    target_tokens = _token_set(target)
    candidate_tokens = _token_set(candidate)

    token_score = jaccard_similarity(target_tokens, candidate_tokens)

    target_title_tokens = set(target.clean_title.split())
    candidate_title_tokens = set(candidate.clean_title.split())
    title_score = jaccard_similarity(target_title_tokens, candidate_title_tokens)

    confidence = round((0.7 * token_score) + (0.3 * title_score), 4)

    shared_tokens = sorted(target_tokens & candidate_tokens)
    if shared_tokens:
        reason = f"Shared tokens: {', '.join(shared_tokens[:8])}"
    else:
        reason = "Low lexical overlap"

    return DuplicateCandidate(
        issue_id=candidate.issue_id,
        confidence=confidence,
        reason=reason,
    )


def find_duplicate_candidates(
    target: NormalizedIssue,
    corpus: list[NormalizedIssue],
    *,
    top_n: int = 3,
) -> list[DuplicateCandidate]:
    """
    Return the best duplicate candidates for a target issue.
    """
    scored: list[DuplicateCandidate] = []

    for candidate in corpus:
        if candidate.issue_id == target.issue_id:
            continue

        result = score_duplicate_pair(target, candidate)
        if result.confidence > 0.0:
            scored.append(result)

    scored.sort(key=lambda item: (-item.confidence, item.issue_id))
    return scored[:top_n]
