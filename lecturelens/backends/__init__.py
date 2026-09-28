"""
Backend factory with strict availability checks.
All factories log why each backend was skipped.
Simulated backends can NEVER be returned from get_*_backend() functions
unless the caller explicitly requests demo mode.
"""

from lecturelens.backends.base import STTBackend, LLMBackend, EmbedBackend, BackendUnavailable
from lecturelens.logging_setup import logger


def get_stt_backend(preference: str = "auto") -> STTBackend:
    """Factory: STT backend, NPU first, CPU fallback.
    Raises BackendUnavailable if no real backend can be loaded.
    """
    if preference in ("auto", "npu"):
        try:
            from lecturelens.backends.stt_qnn import QNNWhisperBackend
            backend = QNNWhisperBackend()
            backend.load()
            if backend.info.verified_npu:
                logger.info("STT factory: using QNN NPU backend.")
                return backend
        except BackendUnavailable as e:
            logger.warning(f"STT factory: QNN backend unavailable ({e}). Trying CPU.")
        except Exception as e:
            logger.warning(f"STT factory: QNN backend error ({e}). Trying CPU.")

    if preference in ("auto", "cpu"):
        try:
            from lecturelens.backends.stt_cpu import CPUWhisperBackend
            backend = CPUWhisperBackend()
            backend.load()
            if backend.info.is_real:
                logger.info("STT factory: using real CPU Whisper backend.")
                return backend
            logger.warning("STT factory: CPU Whisper model files not found. STT unavailable.")
            raise BackendUnavailable(
                "Whisper ONNX model files not found. Run: python scripts/download_models.py"
            )
        except BackendUnavailable:
            raise
        except Exception as e:
            raise BackendUnavailable(f"STT CPU backend failed to load: {e}")

    raise BackendUnavailable(f"Unknown STT backend preference: {preference}")


def get_llm_backend(preference: str = "auto") -> LLMBackend:
    """Factory: LLM backend, Foundry/NPU first, CPU (Ollama/llama.cpp) fallback.
    Raises BackendUnavailable if no real engine is reachable.
    """
    if preference in ("auto", "npu"):
        try:
            from lecturelens.backends.llm_foundry import FoundryLLMBackend
            backend = FoundryLLMBackend()
            backend.load()
            logger.info(
                f"LLM factory: using Foundry Local backend "
                f"(verified_npu={backend.info.verified_npu})."
            )
            return backend
        except BackendUnavailable as e:
            logger.warning(f"LLM factory: Foundry backend unavailable ({e}). Trying CPU engine.")
        except Exception as e:
            logger.warning(f"LLM factory: Foundry backend error ({e}). Trying CPU engine.")

    if preference in ("auto", "cpu"):
        try:
            from lecturelens.backends.llm_cpu import CPULLMBackend
            backend = CPULLMBackend()
            backend.load()
            logger.info("LLM factory: using real CPU LLM backend.")
            return backend
        except BackendUnavailable:
            raise
        except Exception as e:
            raise BackendUnavailable(f"CPU LLM backend failed to load: {e}")

    raise BackendUnavailable(f"Unknown LLM backend preference: {preference}")


def get_embed_backend(preference: str = "auto") -> EmbedBackend:
    """Factory: embedding backend.
    Raises BackendUnavailable if no real ONNX model is present.
    """
    try:
        from lecturelens.backends.embed_onnx import ONNXEmbedBackend
        backend = ONNXEmbedBackend(preference=preference)
        backend.load()
        logger.info(f"Embed factory: using ONNX embed backend (is_real={backend.info.is_real}).")
        return backend
    except BackendUnavailable as e:
        raise BackendUnavailable(
            f"Embedding backend unavailable: {e}\n"
            "Run: python scripts/download_models.py"
        )
    except Exception as e:
        raise BackendUnavailable(f"Embedding backend failed: {e}")
