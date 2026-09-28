"""
Backend factory and backend loaders for LectureLens.
"""

from lecturelens.backends.base import STTBackend, LLMBackend, EmbedBackend
from lecturelens.logging_setup import logger

def get_stt_backend(preference: str = "auto") -> STTBackend:
    """Factory to retrieve STT backend (NPU path with CPU fallback)."""
    if preference in ("auto", "npu"):
        try:
            from lecturelens.backends.stt_qnn import QNNWhisperBackend
            backend = QNNWhisperBackend()
            backend.load()
            if backend.info.verified_npu:
                logger.info("Successfully loaded QNN STT Backend on NPU.")
                return backend
            else:
                logger.warning("QNN STT Backend loaded, but NPU verification failed. Falling back to CPU backend.")
        except Exception as e:
            logger.warning(f"Failed to initialize QNN STT Backend ({e}). Falling back to CPU backend.")

    from lecturelens.backends.stt_cpu import CPUWhisperBackend
    backend = CPUWhisperBackend()
    backend.load()
    return backend

def get_llm_backend(preference: str = "auto") -> LLMBackend:
    """Factory to retrieve LLM backend (Foundry Local with CPU fallback)."""
    if preference in ("auto", "npu"):
        try:
            from lecturelens.backends.llm_foundry import FoundryLLMBackend
            backend = FoundryLLMBackend()
            backend.load()
            if backend.info.verified_npu:
                logger.info("Successfully loaded Foundry Local LLM Backend (NPU variant).")
                return backend
            logger.info("Foundry Local LLM Backend loaded (CPU variant).")
            return backend
        except Exception as e:
            logger.warning(f"Failed to load Foundry Local LLM Backend ({e}). Falling back to CPU LLM backend.")

    from lecturelens.backends.llm_cpu import CPULLMBackend
    backend = CPULLMBackend()
    backend.load()
    return backend

def get_embed_backend(preference: str = "auto") -> EmbedBackend:
    """Factory to retrieve Embedding backend."""
    try:
        from lecturelens.backends.embed_onnx import ONNXEmbedBackend
        backend = ONNXEmbedBackend(preference=preference)
        backend.load()
        return backend
    except Exception as e:
        logger.warning(f"Failed to load ONNX Embedding Backend ({e}).")
        raise e
