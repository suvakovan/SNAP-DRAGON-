"""Edge-case tests for Voice Activity Detection module."""

import numpy as np
import pytest
from lecturelens.audio.vad import compute_frame_energy, is_speech, detect_speech_spans


class TestComputeFrameEnergy:
    def test_empty_audio(self):
        result = compute_frame_energy(np.array([], dtype=np.float32))
        assert len(result) == 0

    def test_short_audio(self):
        audio = np.ones(100, dtype=np.float32) * 0.5
        result = compute_frame_energy(audio, frame_length=512)
        assert len(result) == 1

    def test_silence_energy_near_zero(self):
        silence = np.zeros(16000, dtype=np.float32)
        energies = compute_frame_energy(silence, frame_length=512)
        assert np.all(energies < 1e-6)

    def test_tone_energy_positive(self):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        energies = compute_frame_energy(tone, frame_length=512)
        assert np.all(energies > 0.01)


class TestIsSpeech:
    def test_silence_not_speech(self):
        assert not is_speech(np.zeros(16000, dtype=np.float32), threshold=0.01)

    def test_tone_is_speech(self):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        assert is_speech(tone, threshold=0.01)

    def test_empty_not_speech(self):
        assert not is_speech(np.array([], dtype=np.float32))


class TestDetectSpeechSpans:
    def test_empty_audio(self):
        assert detect_speech_spans(np.array([], dtype=np.float32)) == []

    def test_continuous_tone(self):
        t = np.linspace(0, 2.0, 32000, endpoint=False)
        tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        spans = detect_speech_spans(tone, sample_rate=16000, threshold=0.01)
        assert len(spans) >= 1

    def test_silence_only(self):
        silence = np.zeros(32000, dtype=np.float32)
        spans = detect_speech_spans(silence, sample_rate=16000, threshold=0.01)
        assert len(spans) == 0
