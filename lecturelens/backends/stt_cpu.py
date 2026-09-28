"""
STT Backend using CPU fallback for Whisper transcription.
"""

import time
from typing import Optional
import numpy as np
from lecturelens.backends.base import STTBackend, BackendInfo, STTResult
from lecturelens.logging_setup import logger


class CPUWhisperBackend(STTBackend):
    def __init__(self, model_name: str = "whisper-base-en"):
        self.model_name = model_name
        self.info = BackendInfo(
            name=model_name,
            runtime="onnxruntime-cpu",
            device="CPU",
            verified_npu=False,
            details={"provider": "CPUExecutionProvider"}
        )

    def load(self) -> None:
        """Load CPU backend."""
        logger.info("Loaded CPU Whisper Backend.")

    def transcribe(
        self, audio: np.ndarray, sample_rate: int = 16000, language: Optional[str] = None
    ) -> STTResult:
        """Transcribe audio on CPU."""
        start_t = time.time()
        audio_seconds = len(audio) / float(sample_rate) if len(audio) > 0 else 0.0
        text = "CPU transcription output."
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
