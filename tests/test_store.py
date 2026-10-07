"""Tests for session storage operations."""

import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.notes import KeyTerm
from lecturelens.storage.store import save_session, load_session, delete_session


def _make_session(sid="store-test-001"):
    return LectureSession(
        metadata=SessionMetadata(
            id=sid, title="Store Test", created_at="2026-01-01T00:00:00",
            audio_duration_seconds=10.0, total_processing_seconds=1.0,
            stt_backend={"device": "CPU"}, llm_backend={"device": "CPU"},
            embed_backend={"device": "CPU"},
        ),
        transcript="Test transcript.", segments=[],
        summary=["Point 1"],
        key_terms=[KeyTerm(term="Test", definition="A test.")],
        revision_paragraph="Review.", quiz=[], flashcards=[],
        timing_metrics={"total": 1.0},
    )


class TestSessionStore:
    def test_save_and_load(self, tmp_path):
        session = _make_session()
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            path = save_session(session)
            assert path.exists()
            loaded = load_session(session.metadata.id)
            assert loaded is not None
            assert loaded.metadata.title == "Store Test"

    def test_load_nonexistent(self, tmp_path):
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            result = load_session("nonexistent-id")
            assert result is None

    def test_delete(self, tmp_path):
        session = _make_session()
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            save_session(session)
            assert delete_session(session.metadata.id)
            assert not (tmp_path / f"{session.metadata.id}.json").exists()
