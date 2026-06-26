from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StateStore:
    """
    Small SQLite-backed store for idempotency and bot state.
    """

    db_path: Path

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    event_id TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issue_actions (
                    repository TEXT NOT NULL,
                    issue_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (repository, issue_id, action_type)
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issue_fingerprints (
                    repository TEXT NOT NULL,
                    issue_id INTEGER NOT NULL,
                    fingerprint TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (repository, issue_id)
                )
                """)

    def has_processed_event(self, event_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            return row is not None

    def mark_event_processed(self, event_id: str, repository: str, created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO processed_events (event_id, repository, created_at)
                VALUES (?, ?, ?)
                """,
                (event_id, repository, created_at),
            )

    def record_issue_fingerprint(
        self,
        repository: str,
        issue_id: int,
        fingerprint: str,
        created_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO issue_fingerprints
                (repository, issue_id, fingerprint, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (repository, issue_id, fingerprint, created_at),
            )

    def get_issue_fingerprint(self, repository: str, issue_id: int) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT fingerprint
                FROM issue_fingerprints
                WHERE repository = ? AND issue_id = ?
                """,
                (repository, issue_id),
            ).fetchone()
            if row is None:
                return None
            return str(row["fingerprint"])

    def has_action(self, repository: str, issue_id: int, action_type: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM issue_actions
                WHERE repository = ? AND issue_id = ? AND action_type = ?
                """,
                (repository, issue_id, action_type),
            ).fetchone()
            return row is not None

    def record_action(
        self,
        repository: str,
        issue_id: int,
        action_type: str,
        action_hash: str,
        created_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO issue_actions
                (repository, issue_id, action_type, action_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (repository, issue_id, action_type, action_hash, created_at),
            )
