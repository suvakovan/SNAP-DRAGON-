"""Edge-case tests for audio chunker module."""

import numpy as np
from lecturelens.audio.chunker import chunk_audio


class TestChunkAudio:
    def test_empty_array(self):
        assert chunk_audio(np.array([], dtype=np.float32)) == []

    def test_short_audio_single_chunk(self):
        audio = np.random.randn(8000).astype(np.float32)
        chunks = chunk_audio(audio, sample_rate=16000, chunk_seconds=30.0)
        assert len(chunks) == 1
        assert chunks[0][0] == 0.0

    def test_exact_chunk_boundary(self):
        audio = np.random.randn(16000 * 30).astype(np.float32)
        chunks = chunk_audio(audio, sample_rate=16000, chunk_seconds=30.0)
        assert len(chunks) >= 1

    def test_multiple_chunks(self):
        audio = np.random.randn(16000 * 90).astype(np.float32)
        chunks = chunk_audio(audio, sample_rate=16000, chunk_seconds=30.0, overlap_seconds=1.0)
        assert len(chunks) >= 3

    def test_chunk_data_not_empty(self):
        audio = np.random.randn(16000 * 60).astype(np.float32)
        chunks = chunk_audio(audio, sample_rate=16000, chunk_seconds=30.0)
        for start, end, data in chunks:
            assert len(data) > 0
            assert end > start
