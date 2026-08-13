from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from triagecraft.models import (
    BotDecision,
    DuplicateCandidate,
    Issue,
    LabelSuggestion,
    NormalizedIssue,
    ProcessingResult,
    RepositoryConfig,
    Summary,
)


def test_issue_model_accepts_valid_data() -> None:
    issue = Issue(
        id=1,
        number=1,
        repository="owner/repo",
        title="Bug report",
        body="Something is broken",
        author="alice",
        labels=["bug"],
        created_at=datetime.now(timezone.utc),
    )
    assert issue.id == 1
    assert issue.number == 1
    assert issue.repository == "owner/repo"
    assert issue.labels == ["bug"]


def test_issue_model_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Issue(
            id=1,
            number=1,
            repository="owner/repo",
            title="Bug report",
            body="Something is broken",
            author="alice",
            labels=[],
            created_at=datetime.now(timezone.utc),
            unexpected="nope",  # type: ignore[call-arg]
        )


def test_duplicate_candidate_confidence_bounds() -> None:
    candidate = DuplicateCandidate(issue_id=2, confidence=0.91, reason="Very similar title")
    assert candidate.confidence == 0.91

    with pytest.raises(ValidationError):
        DuplicateCandidate(issue_id=2, confidence=1.5, reason="Too high")


def test_repository_config_defaults_are_safe() -> None:
    config = RepositoryConfig(repository="owner/repo")
    assert config.dry_run is True
    assert "bug" in config.allowed_labels
    assert 0.0 <= config.duplicate_threshold <= 1.0


def test_summary_and_decision_models() -> None:
    summary = Summary(text="Short summary", length=13)
    decision = BotDecision(should_comment=True, should_label=False)

    assert summary.length == 13
    assert decision.should_comment is True
    assert decision.should_label is False


def test_processing_result_can_be_created() -> None:
    normalized = NormalizedIssue(
        issue_id=1,
        clean_title="bug report",
        clean_body="something is broken",
        tokens=["bug", "broken"],
    )

    result = ProcessingResult(
        normalized_issue=normalized,
        duplicate_candidates=[],
        label_suggestions=[LabelSuggestion(label="bug", confidence=0.9)],
        summary=None,
        decision=BotDecision(should_comment=False, should_skip=True),
    )

    assert result.normalized_issue.issue_id == 1
    assert result.decision.should_skip is True
