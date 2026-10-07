"""Tests for study export formats (SRT, Anki CSV, plain transcript)."""

import pytest
import tempfile
from pathlib import Path
from lecturelens.storage.exports import (
    export_anki_csv, export_srt, export_plain_transcript,
    export_study_sheet, _seconds_to_srt_ts,
)
from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.notes import KeyTerm, QuizQuestion, Flashcard


@pytest.fixture
def export_session():
    return LectureSession(
        metadata=SessionMetadata(
            id="exp-001", title="Export Test", created_at="2026-10-07T00:00:00",
            audio_duration_seconds=60.0, total_processing_seconds=3.0,
            stt_backend={"device": "CPU"}, llm_backend={"device": "CPU"},
            embed_backend={"device": "CPU"},
        ),
        transcript="This is a test transcript for export validation.",
        segments=[
            {"start": 0.0, "end": 10.0, "text": "First segment."},
            {"start": 10.0, "end": 20.0, "text": "Second segment."},
        ],
        summary=["Summary point one."],
        key_terms=[KeyTerm(term="Export", definition="To save in external format.")],
        revision_paragraph="Review export formats.",
        quiz=[QuizQuestion(
            question="What is an export?", options=["Save", "Delete", "Load", "Copy"],
            correct_index=0, explanation="Export means to save.",
        )],
        flashcards=[Flashcard(question="What is SRT?", answer="SubRip subtitle format.")],
        timing_metrics={},
    )


class TestSRTTimestamp:
    def test_zero(self):
        assert _seconds_to_srt_ts(0.0) == "00:00:00,000"

    def test_one_minute(self):
        assert _seconds_to_srt_ts(60.0) == "00:01:00,000"

    def test_fractional(self):
        assert _seconds_to_srt_ts(1.5) == "00:00:01,500"


class TestExports:
    def test_anki_csv(self, export_session):
        with tempfile.TemporaryDirectory() as td:
            path = export_anki_csv(export_session, output_dir=Path(td))
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "SRT" in content

    def test_srt(self, export_session):
        with tempfile.TemporaryDirectory() as td:
            path = export_srt(export_session, output_dir=Path(td))
            assert path.exists()
            assert "-->" in path.read_text(encoding="utf-8")

    def test_plain_transcript(self, export_session):
        with tempfile.TemporaryDirectory() as td:
            path = export_plain_transcript(export_session, output_dir=Path(td))
            assert path.exists()

    def test_study_sheet(self, export_session):
        with tempfile.TemporaryDirectory() as td:
            path = export_study_sheet(export_session, output_dir=Path(td))
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "Summary" in content
            assert "Quiz" in content
