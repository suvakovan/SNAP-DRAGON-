"""
Tests for audio loading, preprocessing, VAD, and recorder.
"""

import numpy as np
import pytest
from lecturelens.audio.preprocess import preprocess_audio
from lecturelens.audio.vad import detect_speech_spans, is_speech


def create_synthetic_audio(duration_sec: float = 30.0, sample_rate: int = 16000) -> np.ndarray:
    """Creates synthetic audio: 5s silence, 10s tone burst, 5s silence, 10s tone burst."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    audio = np.zeros_like(t, dtype=np.float32)

    # Burst 1: 5s to 15s (440 Hz tone)
    idx1 = (t >= 5.0) & (t <= 15.0)
    audio[idx1] = 0.5 * np.sin(2 * np.pi * 440 * t[idx1])

    # Burst 2: 20s to 30s (880 Hz tone)
    idx2 = (t >= 20.0) & (t <= 30.0)
    audio[idx2] = 0.5 * np.sin(2 * np.pi * 880 * t[idx2])

    return audio


def test_preprocess_audio():
    # Test stereo resample and normalization
    stereo_audio = np.random.randn(44100, 2).astype(np.float32) * 2.0
    processed = preprocess_audio(stereo_audio, original_sample_rate=44100, target_sample_rate=16000)

    assert processed.ndim == 1
    assert len(processed) == 16000
    assert np.max(np.abs(processed)) <= 1.0
    assert processed.dtype == np.float32


def test_vad_detects_speech_bursts():
    audio = create_synthetic_audio(duration_sec=30.0, sample_rate=16000)
    spans = detect_speech_spans(audio, sample_rate=16000, threshold=0.01)

    assert len(spans) >= 2
    # Verify span 1 is around 5s-15s
    assert any(4.5 <= start <= 5.5 for start, end in spans)
    # Verify silent region (0s-4s) returns False for is_speech
    silence = audio[: 4 * 16000]
    assert not is_speech(silence, threshold=0.01)
