"""
STT Backend using Qualcomm QNN / ONNX Runtime HTP Execution Provider.
"""

import time
from typing import Optional
import numpy as np
from lecturelens.backends.base import STTBackend, BackendInfo, STTResult
from lecturelens.logging_setup import logger


class QNNWhisperBackend(STTBackend):
    def __init__(self, model_name: str = "whisper-base-en"):
        self.model_name = model_name
        self.info = BackendInfo(
            name=model_name,
            runtime="onnxruntime-qnn",
            device="NPU",
            verified_npu=False,
            details={"provider": "QNNExecutionProvider", "backend": "HTP"}
        )
        self.session = None

    def load(self) -> None:
        """Attempt to load ORT session with QNNExecutionProvider."""
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if "QNNExecutionProvider" not in providers:
                logger.warning("QNNExecutionProvider not present in available ONNX Runtime providers.")
                self.info.verified_npu = False
                return

            # Test provider options for QNN HTP
            qnn_options = {
                "backend_path": "QnnHtp.dll",
                "htp_performance_mode": "high_performance"
            }
            # Note: actual model loading will verify session providers
            self.info.details["providers"] = providers
            self.info.details["qnn_options"] = qnn_options
            self.info.verified_npu = True
            logger.info("QNN Whisper backend verified available.")
        except Exception as e:
            logger.warning(f"Error checking QNN Whisper backend: {e}")
            self.info.verified_npu = False

    def transcribe(
        self, audio: np.ndarray, sample_rate: int = 16000, language: Optional[str] = None
    ) -> STTResult:
        """Transcribe audio array using QNN model."""
        if not self.info.verified_npu:
            raise RuntimeError("QNN NPU backend is not verified or loaded.")

        start_t = time.time()
        audio_seconds = len(audio) / float(sample_rate)
        # Mock/placeholder implementation for scaffold
        text = "QNN STT placeholder transcription."
        wall_seconds = time.time() - start_t
        rtf = wall_seconds / max(audio_seconds, 0.001)

        return STTResult(
            text=text,
            segments=[{"start": 0.0, "end": audio_seconds, "text": text}],
            language=language or "en",
            audio_seconds=audio_seconds,
            wall_seconds=wall_seconds,
            rtf=rtf
        )
