"""Tests for session Pydantic models and serialization."""

import json
import pytest
from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.notes import KeyTerm, QuizQuestion, Flashcard


def _make_session(**overrides):
    defaults = dict(
        metadata=SessionMetadata(
            id="s-001", title="Test", created_at="2026-01-01T00:00:00",
            audio_duration_seconds=10.0, total_processing_seconds=2.0,
            stt_backend={"device": "CPU"}, llm_backend={"device": "CPU"},
            embed_backend={"device": "CPU"},
        ),
        transcript="Hello world.", segments=[], summary=["Point 1"],
        key_terms=[KeyTerm(term="AI", definition="Artificial Intelligence")],
        revision_paragraph="Review AI.", quiz=[], flashcards=[],
        timing_metrics={"stt_wall_seconds": 1.0},
    )
    defaults.update(overrides)
    return LectureSession(**defaults)


class TestSessionModel:
    def test_roundtrip_serialization(self):
        session = _make_session()
        data = json.loads(session.model_dump_json())
        restored = LectureSession(**data)
        assert restored.metadata.id == "s-001"
        assert restored.transcript == "Hello world."

    def test_metadata_fields(self):
        session = _make_session()
        assert session.metadata.title == "Test"
        assert session.metadata.audio_duration_seconds == 10.0

    def test_empty_quiz_and_flashcards(self):
        session = _make_session(quiz=[], flashcards=[])
        assert len(session.quiz) == 0
        assert len(session.flashcards) == 0

    def test_key_terms_access(self):
        session = _make_session()
        assert session.key_terms[0].term == "AI"
