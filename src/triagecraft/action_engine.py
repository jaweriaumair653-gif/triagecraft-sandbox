from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Protocol

from triagecraft.comment_templates import (
    format_duplicate_comment,
    format_info_request_comment,
    format_label_comment,
    format_summary_comment,
)
from triagecraft.models import ProcessingResult, RepositoryConfig
from triagecraft.state_store import StateStore

logger = logging.getLogger(__name__)


class GitHubActionsClient(Protocol):
    def add_labels(
        self,
        repo_full_name: str,
        issue_number: int,
        labels: Sequence[str],
    ) -> list[str]: ...

    def post_comment(
        self,
        repo_full_name: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]: ...


@dataclass(slots=True)
class ActionResult:
    labels_applied: bool = False
    comment_posted: bool = False
    event_recorded: bool = False


class ActionEngine:
    """
    Execute a triage result safely and idempotently.
    """

    def __init__(
        self,
        config: RepositoryConfig,
        client: GitHubActionsClient,
        store: StateStore,
    ) -> None:
        self.config = config
        self.client = client
        self.store = store

    def execute(
        self,
        *,
        repository: str,
        issue_id: int,
        result: ProcessingResult,
        event_id: str | None = None,
        event_created_at: str | None = None,
    ) -> ActionResult:
        """
        Apply labels/comments for one processed issue.

        Dry-run mode and repeated actions are skipped safely.
        """
        start_time = time.perf_counter()

        if result.decision.should_skip or self.config.dry_run:
            logger.info(
                "Skipping actions for %s#%s (dry_run=%s, should_skip=%s)",
                repository,
                issue_id,
                self.config.dry_run,
                result.decision.should_skip,
            )
            return ActionResult()

        if event_id is not None and self.store.has_processed_event(event_id):
            logger.info(
                "Skipping actions for %s#%s because event %s was already processed",
                repository,
                issue_id,
                event_id,
            )
            return ActionResult(event_recorded=True)

        labels = self.select_labels(result)
        comment_body = self._build_comment_body(result, labels)

        action_result = ActionResult()

        logger.info(
            "ActionEngine start repository=%s issue=%s labels=%s comment=%s event_id=%s",
            repository,
            issue_id,
            labels,
            bool(comment_body),
            event_id,
        )

        if labels and not self.store.has_action(repository, issue_id, "labels"):
            t_labels = time.perf_counter()
            self.client.add_labels(repository, issue_id, labels)
            labels_ms = (time.perf_counter() - t_labels) * 1000
            self.store.record_action(
                repository=repository,
                issue_id=issue_id,
                action_type="labels",
                action_hash=self._hash_text(",".join(labels)),
                created_at=self._now_iso(),
            )
            logger.info(
                "Applied labels %s to %s#%s in %.2f ms",
                labels,
                repository,
                issue_id,
                labels_ms,
            )
            action_result.labels_applied = True

        if comment_body and not self.store.has_action(repository, issue_id, "comment"):
            t_comment = time.perf_counter()
            self.client.post_comment(repository, issue_id, comment_body)
            comment_ms = (time.perf_counter() - t_comment) * 1000
            self.store.record_action(
                repository=repository,
                issue_id=issue_id,
                action_type="comment",
                action_hash=self._hash_text(comment_body),
                created_at=self._now_iso(),
            )
            logger.info(
                "Posted comment to %s#%s in %.2f ms",
                repository,
                issue_id,
                comment_ms,
            )
            action_result.comment_posted = True

        if event_id is not None and event_created_at is not None:
            self.store.mark_event_processed(event_id, repository, event_created_at)
            logger.info("Recorded event %s for %s#%s", event_id, repository, issue_id)
            action_result.event_recorded = True

        total_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "ActionEngine complete repository=%s issue=%s labels_applied=%s comment_posted=%s total_ms=%.2f",
            repository,
            issue_id,
            action_result.labels_applied,
            action_result.comment_posted,
            total_ms,
        )

        return action_result

    def select_labels(self, result: ProcessingResult) -> list[str]:
        return self._select_labels(result)

    def _select_labels(self, result: ProcessingResult) -> list[str]:
        labels: list[str] = []

        for suggestion in result.label_suggestions:
            if suggestion.confidence < self.config.label_threshold:
                continue
            if suggestion.label in labels:
                continue
            labels.append(suggestion.label)

        return labels[:3]

    def _build_comment_body(
        self,
        result: ProcessingResult,
        labels: Sequence[str],
    ) -> str:
        sections: list[str] = []

        top_duplicate = result.duplicate_candidates[0] if result.duplicate_candidates else None
        if (
            top_duplicate is not None
            and top_duplicate.confidence >= self.config.duplicate_threshold
        ):
            sections.append(
                format_duplicate_comment(
                    result.normalized_issue,
                    result.duplicate_candidates,
                )
            )

        if result.summary is not None and result.summary.text.strip():
            sections.append(format_summary_comment(result.summary))

        if result.decision.should_request_info:
            sections.append(format_info_request_comment(result.normalized_issue))

        if labels:
            label_suggestions = [
                suggestion for suggestion in result.label_suggestions if suggestion.label in labels
            ]
            sections.append(format_label_comment(label_suggestions))

        return "\n\n".join(section for section in sections if section.strip()).strip()

    @staticmethod
    def _hash_text(value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
