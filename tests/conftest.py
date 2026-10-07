"""Shared pytest fixtures for LectureLens test suite."""

import numpy as np
import pytest
from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.notes import KeyTerm, QuizQuestion, Flashcard


@pytest.fixture
def sample_audio_silence():
    """1 second of silence at 16kHz."""
    return np.zeros(16000, dtype=np.float32)


@pytest.fixture
def sample_audio_tone():
    """1 second 440Hz sine tone at 16kHz."""
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    return (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


@pytest.fixture
def sample_audio_long():
    """30 seconds with speech-like bursts."""
    sr = 16000
    t = np.linspace(0, 30.0, sr * 30, endpoint=False)
    audio = np.zeros_like(t, dtype=np.float32)
    audio[(t >= 2.0) & (t < 12.0)] = 0.4 * np.sin(2 * np.pi * 440 * t[(t >= 2.0) & (t < 12.0)])
    audio[(t >= 18.0) & (t < 28.0)] = 0.4 * np.sin(2 * np.pi * 880 * t[(t >= 18.0) & (t < 28.0)])
    return audio


@pytest.fixture
def mock_session():
    """Pre-built LectureSession for testing."""
    return LectureSession(
        metadata=SessionMetadata(
            id="test-session-001",
            title="Test Lecture on NPUs",
            created_at="2026-10-07T12:00:00",
            audio_duration_seconds=30.0,
            total_processing_seconds=5.0,
            stt_backend={"device": "CPU", "verified_npu": False},
            llm_backend={"device": "CPU", "verified_npu": False},
            embed_backend={"device": "CPU", "verified_npu": False},
        ),
        transcript="Neural Processing Units accelerate on-device AI inference with low power consumption.",
        segments=[{"start": 0.0, "end": 30.0, "text": "Neural Processing Units accelerate on-device AI."}],
        summary=["NPUs accelerate AI inference locally.", "Low power consumption extends battery life."],
        key_terms=[KeyTerm(term="NPU", definition="Neural Processing Unit for AI inference.")],
        revision_paragraph="Review NPU architecture and power efficiency benefits.",
        quiz=[
            QuizQuestion(
                question="What does NPU stand for?",
                options=["Neural Processing Unit", "Network Protocol Utility", "Numeric Processor Unit", "Node Package Updater"],
                correct_index=0,
                explanation="NPU stands for Neural Processing Unit.",
            )
        ],
        flashcards=[Flashcard(question="What is an NPU?", answer="A Neural Processing Unit for AI inference.")],
        timing_metrics={"stt_wall_seconds": 2.0, "stt_rtf": 0.066, "total_pipeline_seconds": 5.0},
    )
