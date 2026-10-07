"""Tests for BackendInfo dataclass and base classes."""

import numpy as np
import pytest
from lecturelens.backends.base import (
    BackendInfo, STTResult, LLMResult, BackendUnavailable,
)


class TestBackendInfo:
    def test_creation(self):
        info = BackendInfo(
            name="test-model", runtime="test-runtime",
            device="CPU", verified_npu=False,
        )
        assert info.name == "test-model"
        assert info.device == "CPU"
        assert not info.verified_npu

    def test_defaults(self):
        info = BackendInfo(
            name="m", runtime="r", device="CPU", verified_npu=False,
        )
        assert info.is_real is False
        assert info.is_simulated is True
        assert info.details == {}

    def test_npu_info(self):
        info = BackendInfo(
            name="whisper", runtime="qnn", device="NPU",
            verified_npu=True, is_real=True, is_simulated=False,
        )
        assert info.verified_npu
        assert info.is_real


class TestSTTResult:
    def test_creation(self):
        result = STTResult(
            text="hello", segments=[], language="en",
            audio_seconds=5.0, wall_seconds=1.0, rtf=0.2,
        )
        assert result.text == "hello"
        assert result.rtf == 0.2


class TestLLMResult:
    def test_creation(self):
        result = LLMResult(
            text="response", prompt_tokens=10, completion_tokens=20,
            time_to_first_token=0.5, total_seconds=2.0, tokens_per_second=10.0,
        )
        assert result.tokens_per_second == 10.0


class TestBackendUnavailable:
    def test_is_runtime_error(self):
        with pytest.raises(RuntimeError):
            raise BackendUnavailable("not installed")
