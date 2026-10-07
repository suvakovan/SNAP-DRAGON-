"""Edge-case tests for audio preprocessing pipeline."""

import numpy as np
import pytest
from lecturelens.audio.preprocess import preprocess_audio, load_audio, resample_audio


class TestPreprocessAudio:
    def test_mono_passthrough(self):
        mono = np.random.randn(16000).astype(np.float32)
        result = preprocess_audio(mono, 16000, 16000)
        assert result.ndim == 1
        assert result.dtype == np.float32

    def test_stereo_to_mono(self):
        stereo = np.random.randn(16000, 2).astype(np.float32)
        result = preprocess_audio(stereo, 16000, 16000)
        assert result.ndim == 1

    def test_peak_normalization(self):
        loud = np.ones(16000, dtype=np.float32) * 5.0
        result = preprocess_audio(loud, 16000, 16000)
        assert np.max(np.abs(result)) <= 1.0 + 1e-6

    def test_empty_audio(self):
        empty = np.array([], dtype=np.float32)
        result = preprocess_audio(empty, 16000, 16000)
        assert len(result) == 0

    def test_resample_44100_to_16000(self):
        audio = np.random.randn(44100).astype(np.float32)
        result = resample_audio(audio, 44100, 16000)
        assert len(result) == 16000

    def test_resample_same_rate(self):
        audio = np.random.randn(16000).astype(np.float32)
        result = resample_audio(audio, 16000, 16000)
        assert len(result) == 16000

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_audio("nonexistent_audio_file.wav")

    def test_multichannel_averaging(self):
        multi = np.random.randn(8000, 4).astype(np.float32)
        result = preprocess_audio(multi, 8000, 16000)
        assert result.ndim == 1
