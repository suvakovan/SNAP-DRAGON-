"""
STT Backend using Qualcomm QNN / ONNX Runtime HTP Execution Provider.

verified_npu is set True ONLY when:
  - QNNExecutionProvider is the FIRST active provider in the session
  - The model file exists and is loaded
  - A real decode run completes
"""

import time
from pathlib import Path
from typing import Optional
import numpy as np

from lecturelens.backends.base import STTBackend, BackendInfo, STTResult, BackendUnavailable
from lecturelens.config import config
from lecturelens.logging_setup import logger

_MODEL_DIR = config.models_dir / "whisper-base-en"
_ENCODER_PATH = _MODEL_DIR / "encoder.onnx"
_DECODER_PATH = _MODEL_DIR / "decoder.onnx"


class QNNWhisperBackend(STTBackend):
    def __init__(self, model_name: str = "whisper-base-en"):
        self.model_name = model_name
        self.info = BackendInfo(
            name=model_name,
            runtime="onnxruntime-qnn",
            device="NPU",
            verified_npu=False,
            is_real=False,
            is_simulated=True,
            details={
                "encoder_path": str(_ENCODER_PATH),
                "decoder_path": str(_DECODER_PATH)
            }
        )
        self._encoder = None
        self._decoder = None
        self._loaded = False

    def load(self) -> None:
        """Load ORT session with QNNExecutionProvider (HTP).
        Sets verified_npu=True only when QNN is genuinely the first active provider.
        """
        try:
            import onnxruntime as ort
        except ImportError:
            raise BackendUnavailable("onnxruntime not installed.")

        available = ort.get_available_providers()
        if "QNNExecutionProvider" not in available:
            self.info.verified_npu = False
            self.info.details["npu_unverified_reason"] = (
                "QNNExecutionProvider absent from ort.get_available_providers(). "
                "Install onnxruntime-qnn or update QNN drivers."
            )
            raise BackendUnavailable(
                "QNNExecutionProvider not available. Falling back to CPU."
            )

        if not _ENCODER_PATH.exists() or not _DECODER_PATH.exists():
            self.info.details["npu_unverified_reason"] = "Whisper model files not found"
            raise BackendUnavailable(
                f"Whisper ONNX model files not found in {_MODEL_DIR}.\n"
                f"Run: python scripts/download_models.py"
            )

        qnn_options = {
            "backend_path": "QnnHtp.dll",
            "htp_performance_mode": "high_performance",
        }

        try:
            opts = ort.SessionOptions()
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self._encoder = ort.InferenceSession(
                str(_ENCODER_PATH),
                sess_options=opts,
                providers=[("QNNExecutionProvider", qnn_options), "CPUExecutionProvider"]
            )
            self._decoder = ort.InferenceSession(
                str(_DECODER_PATH),
                sess_options=opts,
                providers=[("QNNExecutionProvider", qnn_options), "CPUExecutionProvider"]
            )

            # Verify QNN is the first active provider
            enc_providers = self._encoder.get_providers()
            dec_providers = self._decoder.get_providers()
            self.info.details["encoder_providers"] = enc_providers
            self.info.details["decoder_providers"] = dec_providers

            if enc_providers[0] == "QNNExecutionProvider" and dec_providers[0] == "QNNExecutionProvider":
                self.info.verified_npu = True
                self.info.device = "NPU"
                self.info.is_real = True
                self.info.is_simulated = False
                logger.info(f"QNN Whisper Backend VERIFIED on NPU. Providers: {enc_providers}")
            else:
                self.info.verified_npu = False
                self.info.details["npu_unverified_reason"] = (
                    f"QNN was not first active provider. Encoder: {enc_providers}"
                )
                logger.warning(
                    f"QNN Whisper loaded but QNN is NOT first provider: {enc_providers}. "
                    "Falling back to CPU."
                )
                raise BackendUnavailable("QNN not first active provider — use CPU backend.")

            self._loaded = True

        except BackendUnavailable:
            raise
        except Exception as e:
            self.info.details["load_error"] = str(e)
            self.info.details["npu_unverified_reason"] = f"Session creation error: {e}"
            raise BackendUnavailable(f"QNN session creation failed: {e}")

    def transcribe(
        self, audio: np.ndarray, sample_rate: int = 16000, language: Optional[str] = None
    ) -> STTResult:
        if not self._loaded:
            raise BackendUnavailable("QNN Whisper model is not loaded.")

        from lecturelens.backends.stt_cpu import (
            _compute_log_mel, _greedy_decode
        )

        start_t = time.time()
        audio_seconds = len(audio) / float(sample_rate) if len(audio) > 0 else 0.0

        if audio_seconds == 0:
            return STTResult(
                text="", segments=[], language=language or "en",
                audio_seconds=0.0, wall_seconds=0.0, rtf=0.0
            )

        mel = _compute_log_mel(audio, sample_rate)
        encoder_out = self._encoder.run(None, {"mel": mel})[0]
        text, segments = _greedy_decode(self._decoder, encoder_out, audio_seconds)

        wall_seconds = time.time() - start_t
        rtf = wall_seconds / max(audio_seconds, 0.001)

        return STTResult(
            text=text,
            segments=segments,
            language=language or "en",
            audio_seconds=audio_seconds,
            wall_seconds=wall_seconds,
            rtf=rtf
        )
