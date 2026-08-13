from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)


class Issue(StrictModel):
    id: int
    number: int
    repository: str
    title: str
    body: str | None = None
    author: str
    labels: list[str] = Field(default_factory=list)
    created_at: datetime


class NormalizedIssue(StrictModel):
    issue_id: int
    clean_title: str
    clean_body: str
    tokens: list[str] = Field(default_factory=list)


class DuplicateCandidate(StrictModel):
    issue_id: int
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class LabelSuggestion(StrictModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class Summary(StrictModel):
    text: str
    length: int


class BotDecision(StrictModel):
    should_comment: bool = False
    should_label: bool = False
    should_request_info: bool = False
    should_skip: bool = False


class RepositoryConfig(StrictModel):
    repository: str
    duplicate_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    label_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    summary_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    dry_run: bool = True
    allowed_labels: list[str] = Field(
        default_factory=lambda: ["bug", "feature", "docs", "question"]
    )
    webhook_secret: str | None = None


class WebhookEvent(StrictModel):
    event_type: str
    action: str
    repository: str
    issue: Issue | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ProcessingResult(StrictModel):
    normalized_issue: NormalizedIssue
    duplicate_candidates: list[DuplicateCandidate] = Field(default_factory=list)
    label_suggestions: list[LabelSuggestion] = Field(default_factory=list)
    summary: Summary | None = None
    decision: BotDecision
