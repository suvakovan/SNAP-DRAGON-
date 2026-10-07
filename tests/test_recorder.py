"""Tests for microphone recorder module (non-hardware parts)."""

import numpy as np
from lecturelens.audio.recorder import list_devices, MicRecorder


class TestMicRecorder:
    def test_init_defaults(self):
        rec = MicRecorder()
        assert rec.sample_rate == 16000
        assert rec.device_index is None
        assert not rec.is_active()

    def test_stop_without_start(self):
        rec = MicRecorder()
        result = rec.stop()
        assert len(result) == 0
        assert result.dtype == np.float32

    def test_read_chunk_empty_queue(self):
        rec = MicRecorder()
        chunk = rec.read_chunk(seconds=1.0)
        assert len(chunk) == 0

    def test_list_devices_returns_list(self):
        devices = list_devices()
        assert isinstance(devices, list)
