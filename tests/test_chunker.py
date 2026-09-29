"""
Tests for audio window chunker.
"""

import numpy as np
from lecturelens.audio.chunker import chunk_audio
try:
    from tests.test_audio import create_synthetic_audio
except ImportError:
    try:
        from test_audio import create_synthetic_audio
    except ImportError:
        from .test_audio import create_synthetic_audio


def test_chunker_coverage_and_overlap():
    sample_rate = 16000
    duration_sec = 65.0
    audio = create_synthetic_audio(duration_sec=duration_sec, sample_rate=sample_rate)

    chunks = chunk_audio(audio, sample_rate=sample_rate, chunk_seconds=30.0, overlap_seconds=1.0)

    assert len(chunks) >= 2
    # Verify first chunk start
    assert chunks[0][0] == 0.0
    # Verify total coverage up to end of audio
    assert chunks[-1][1] >= duration_sec - 1.0

    # Verify overlap between consecutive chunks
    for i in range(len(chunks) - 1):
        c1_end = chunks[i][1]
        c2_start = chunks[i + 1][0]
        assert c2_start < c1_end  # Overlap exists
