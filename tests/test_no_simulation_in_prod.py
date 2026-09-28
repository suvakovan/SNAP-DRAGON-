"""
Integrity test: confirms no backend returned by the production factory
has is_simulated=True. This test catches any future regression where
a stub or mock backend is accidentally exposed in production paths.

Uses pytest.mark.unit so it runs in the default suite without hardware.
The factories are expected to raise BackendUnavailable on this machine
since real model files are not present — the test validates the error
type, not the backend, to confirm the factory refuses to yield a simulated backend.
"""

import pytest
from lecturelens.backends.base import BackendUnavailable


@pytest.mark.unit
def test_stt_factory_does_not_return_simulated():
    """STT factory must raise BackendUnavailable (not return a simulated backend)."""
    from lecturelens.backends import get_stt_backend
    try:
        backend = get_stt_backend("cpu")
        # If a backend was returned, it must not be simulated
        assert not backend.info.is_simulated, (
            f"Production STT backend '{backend.info.name}' "
            f"has is_simulated=True — this is forbidden in production."
        )
    except BackendUnavailable:
        # Acceptable: model files are not present on this machine.
        pass


@pytest.mark.unit
def test_llm_factory_does_not_return_simulated():
    """LLM factory must raise BackendUnavailable (not return a simulated backend)."""
    from lecturelens.backends import get_llm_backend
    try:
        backend = get_llm_backend("cpu")
        assert not backend.info.is_simulated, (
            f"Production LLM backend '{backend.info.name}' "
            f"has is_simulated=True — this is forbidden in production."
        )
    except BackendUnavailable:
        pass


@pytest.mark.unit
def test_embed_factory_does_not_return_simulated():
    """Embed factory must raise BackendUnavailable (not return a simulated backend)."""
    from lecturelens.backends import get_embed_backend
    try:
        backend = get_embed_backend()
        assert not backend.info.is_simulated, (
            f"Production Embed backend '{backend.info.name}' "
            f"has is_simulated=True — this is forbidden in production."
        )
    except BackendUnavailable:
        pass


@pytest.mark.unit
def test_determinist_embed_is_flagged_simulated():
    """The test-only DeterministicEmbedBackend must always report is_simulated=True."""
    from lecturelens.backends.embed_onnx import DeterministicEmbedBackend
    b = DeterministicEmbedBackend()
    assert b.info.is_simulated is True
    assert b.info.is_real is False


@pytest.mark.unit
def test_backend_info_fields_exist():
    """BackendInfo must expose is_real and is_simulated fields."""
    from lecturelens.backends.base import BackendInfo
    b = BackendInfo(
        name="test", runtime="test", device="CPU",
        verified_npu=False, is_real=False, is_simulated=True
    )
    assert hasattr(b, "is_real")
    assert hasattr(b, "is_simulated")
    assert b.is_simulated is True
    assert b.is_real is False
