"""
ONNX Embedding Backend — uses a real sentence-transformer ONNX model.

If the real model file is absent, raises BackendUnavailable with download instructions.
Hash-based vectors are ONLY used in unit tests via the DeterministicEmbedBackend,
which must never be returned by the production factory.
"""

from pathlib import Path
from typing import List
import numpy as np

from lecturelens.backends.base import EmbedBackend, BackendInfo, BackendUnavailable
from lecturelens.config import config
from lecturelens.logging_setup import logger

_MODEL_DIR = config.models_dir / "all-MiniLM-L6-v2"
_MODEL_PATH = _MODEL_DIR / "model.onnx"
_TOKENIZER_PATH = _MODEL_DIR / "tokenizer.json"


class ONNXEmbedBackend(EmbedBackend):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", preference: str = "auto"):
        self.model_name = model_name
        self.preference = preference
        self.info = BackendInfo(
            name=model_name,
            runtime="onnxruntime",
            device="CPU",
            verified_npu=False,
            is_real=False,
            is_simulated=True,
            details={
                "model_path": str(_MODEL_PATH),
                "tokenizer_path": str(_TOKENIZER_PATH)
            }
        )
        self._session = None
        self._tokenizer = None

    def load(self) -> None:
        """Load real ONNX embedding model or raise BackendUnavailable."""
        try:
            import onnxruntime as ort
        except ImportError:
            raise BackendUnavailable("onnxruntime not installed. Run: pip install onnxruntime")

        if not _MODEL_PATH.exists():
            raise BackendUnavailable(
                f"Embedding ONNX model not found at {_MODEL_PATH}.\n"
                f"Run: python scripts/download_models.py  to fetch it."
            )

        # Try to load tokenizer (tokenizers library or transformers)
        tokenizer_loaded = False
        if _TOKENIZER_PATH.exists():
            try:
                from tokenizers import Tokenizer
                self._tokenizer = Tokenizer.from_file(str(_TOKENIZER_PATH))
                tokenizer_loaded = True
            except Exception as e:
                logger.warning(f"tokenizers library load failed: {e}")

        if not tokenizer_loaded:
            try:
                from transformers import AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(str(_MODEL_DIR), local_files_only=True)
                tokenizer_loaded = True
            except Exception as e:
                logger.warning(f"transformers tokenizer load failed: {e}")

        if not tokenizer_loaded:
            raise BackendUnavailable(
                f"No tokenizer found for embedding model. Install: pip install tokenizers\n"
                f"And run: python scripts/download_models.py"
            )

        providers = ["CPUExecutionProvider"]
        if "QNNExecutionProvider" in ort.get_available_providers() and self.preference in ("auto", "npu"):
            providers = ["QNNExecutionProvider", "CPUExecutionProvider"]
            self.info.device = "NPU"

        self._session = ort.InferenceSession(str(_MODEL_PATH), providers=providers)
        active_providers = self._session.get_providers()
        self.info.details["active_providers"] = active_providers
        self.info.verified_npu = active_providers[0] == "QNNExecutionProvider"
        self.info.is_real = True
        self.info.is_simulated = False
        logger.info(f"ONNX Embed Backend loaded. Providers: {active_providers}")

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate L2-normalized embeddings using the real ONNX model."""
        if self._session is None or self._tokenizer is None:
            raise BackendUnavailable("Embedding backend not loaded. Call load() first.")

        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        # Tokenize
        if hasattr(self._tokenizer, "batch_encode_plus"):
            # HuggingFace tokenizer
            enc = self._tokenizer(
                texts, padding=True, truncation=True,
                max_length=128, return_tensors="np"
            )
            input_ids = enc["input_ids"].astype(np.int64)
            attention_mask = enc["attention_mask"].astype(np.int64)
            token_type_ids = enc.get("token_type_ids", np.zeros_like(input_ids)).astype(np.int64)
        else:
            # tokenizers library
            encodings = [self._tokenizer.encode(t) for t in texts]
            max_len = max(len(e.ids) for e in encodings)
            input_ids = np.zeros((len(texts), max_len), dtype=np.int64)
            attention_mask = np.zeros((len(texts), max_len), dtype=np.int64)
            token_type_ids = np.zeros((len(texts), max_len), dtype=np.int64)
            for i, e in enumerate(encodings):
                input_ids[i, :len(e.ids)] = e.ids
                attention_mask[i, :len(e.ids)] = 1

        # Run inference
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        }
        outputs = self._session.run(None, inputs)
        # Mean pool last hidden state
        hidden = outputs[0]  # (batch, seq, dim)
        mask = attention_mask[:, :, np.newaxis].astype(np.float32)
        pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)

        # L2 normalize
        norms = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
        return (pooled / norms).astype(np.float32)


class DeterministicEmbedBackend(EmbedBackend):
    """
    Test-only deterministic hash-based embedding backend.
    Produces reproducible normalized vectors for unit tests.
    MUST NOT be returned by the production factory.
    """

    def __init__(self):
        self.info = BackendInfo(
            name="deterministic-test",
            runtime="hash-test",
            device="CPU",
            verified_npu=False,
            is_real=False,
            is_simulated=True,
            details={"use": "UNIT_TEST_ONLY"}
        )

    def load(self) -> None:
        pass  # No real loading needed

    def embed(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            seed = sum(ord(c) for c in text) % 10000
            rng = np.random.RandomState(seed)
            vec = rng.randn(384).astype(np.float32)
            norm = np.linalg.norm(vec)
            vec = vec / max(norm, 1e-6)
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)
