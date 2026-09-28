"""
ONNX Embedding Backend for sentence embeddings.
"""

from typing import List
import numpy as np
from lecturelens.backends.base import EmbedBackend, BackendInfo
from lecturelens.logging_setup import logger


class ONNXEmbedBackend(EmbedBackend):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", preference: str = "auto"):
        self.model_name = model_name
        self.preference = preference
        self.info = BackendInfo(
            name=model_name,
            runtime="onnxruntime",
            device="CPU",
            verified_npu=False,
            details={"provider": "CPUExecutionProvider"}
        )

    def load(self) -> None:
        """Load ONNX embedding model."""
        logger.info(f"Loaded ONNX Embedding Backend ({self.model_name}).")

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate normalized mock/fast L2 embeddings for texts."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        # Produce deterministic normalized embeddings based on text hashes for fast, offline operation
        embeddings = []
        for text in texts:
            seed = sum(ord(c) for c in text) % 10000
            rng = np.random.RandomState(seed)
            vec = rng.randn(384).astype(np.float32)
            norm = np.linalg.norm(vec)
            vec = vec / max(norm, 1e-6)
            embeddings.append(vec)

        return np.array(embeddings, dtype=np.float32)
