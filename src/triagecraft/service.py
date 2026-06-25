from __future__ import annotations

from collections.abc import Sequence

from triagecraft.duplicate_detector import find_duplicate_candidates
from triagecraft.label_suggester import suggest_labels
from triagecraft.models import (
    BotDecision,
    DuplicateCandidate,
    Issue,
    LabelSuggestion,
    NormalizedIssue,
    ProcessingResult,
    RepositoryConfig,
)
from triagecraft.normalizer import normalize_issue
from triagecraft.summarizer import summarize_issue


class TriageService:
    """
    High-level orchestration for triaging a GitHub issue.
    """

    def __init__(self, config: RepositoryConfig) -> None:
        self.config = config

    def process_issue(
        self,
        issue: Issue,
        corpus: Sequence[NormalizedIssue],
    ) -> ProcessingResult:
        """
        Run the full triage pipeline for one issue.
        """
        normalized = normalize_issue(issue)
        duplicate_candidates = find_duplicate_candidates(normalized, list(corpus))
        label_suggestions = suggest_labels(normalized, self.config.allowed_labels)
        summary = summarize_issue(normalized)
        decision = self._decide(normalized, duplicate_candidates, label_suggestions)

        return ProcessingResult(
            normalized_issue=normalized,
            duplicate_candidates=duplicate_candidates,
            label_suggestions=label_suggestions,
            summary=summary,
            decision=decision,
        )

    def _decide(
        self,
        issue: NormalizedIssue,
        duplicate_candidates: list[DuplicateCandidate],
        label_suggestions: list[LabelSuggestion],
    ) -> BotDecision:
        """
        Decide what action the bot should take.

        Dry-run mode always skips actions.
        """
        if self.config.dry_run:
            return BotDecision(should_skip=True)

        top_duplicate = duplicate_candidates[0] if duplicate_candidates else None
        strong_duplicate = (
            top_duplicate is not None
            and top_duplicate.confidence >= self.config.duplicate_threshold
        )

        actionable_labels = [
            suggestion
            for suggestion in label_suggestions
            if suggestion.confidence >= self.config.label_threshold
        ]

        body_word_count = len(issue.clean_body.split())
        should_request_info = not strong_duplicate and body_word_count < 8
        should_label = not strong_duplicate and bool(actionable_labels)
        should_comment = strong_duplicate or should_label or should_request_info

        return BotDecision(
            should_comment=should_comment,
            should_label=should_label,
            should_request_info=should_request_info,
            should_skip=not should_comment and not should_label and not should_request_info,
        )
