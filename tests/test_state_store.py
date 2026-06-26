from __future__ import annotations

from pathlib import Path

from triagecraft.state_store import StateStore


def test_state_store_tracks_events_and_actions(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store = StateStore(db_path)

    assert store.has_processed_event("evt-1") is False

    store.mark_event_processed("evt-1", "owner/repo", "2026-06-24T00:00:00Z")
    assert store.has_processed_event("evt-1") is True

    assert store.get_issue_fingerprint("owner/repo", 7) is None
    store.record_issue_fingerprint("owner/repo", 7, "fingerprint-123", "2026-06-24T00:00:00Z")
    assert store.get_issue_fingerprint("owner/repo", 7) == "fingerprint-123"

    assert store.has_action("owner/repo", 7, "comment") is False
    store.record_action("owner/repo", 7, "comment", "hash-abc", "2026-06-24T00:00:00Z")
    assert store.has_action("owner/repo", 7, "comment") is True


def test_state_store_persists_between_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store1 = StateStore(db_path)
    store1.mark_event_processed("evt-2", "owner/repo", "2026-06-24T00:00:00Z")

    store2 = StateStore(db_path)
    assert store2.has_processed_event("evt-2") is True
