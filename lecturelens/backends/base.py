"""
Core abstract backend interfaces and dataclasses for LectureLens.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class BackendInfo:
    name: str               # e.g. "whisper-base-en"
    runtime: str            # "onnxruntime" | "foundry-local" | "llama.cpp" | "cpu-fallback"
    device: str             # "NPU" | "CPU" | "GPU"
    verified_npu: bool      # True ONLY if NPU/QNN execution provider was confirmed active
    details: Dict[str, Any] = field(default_factory=dict)  # providers, paths, versions


@dataclass
class STTResult:
    text: str
    segments: List[Dict[str, Any]]        # [{start, end, text}]
    language: Optional[str]
    audio_seconds: float
    wall_seconds: float
    rtf: float                            # wall_seconds / audio_seconds (real-time factor)


class STTBackend(ABC):
    info: BackendInfo

    @abstractmethod
    def load(self) -> None:
        """Load model assets into memory/hardware."""
        pass

    @abstractmethod
    def transcribe(
        self, audio: np.ndarray, sample_rate: int = 16000, language: Optional[str] = None
    ) -> STTResult:
        """Transcribe single audio buffer into text and segments."""
        pass


@dataclass
class LLMResult:
    text: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    time_to_first_token: Optional[float]
    total_seconds: float
    tokens_per_second: Optional[float]


class LLMBackend(ABC):
    info: BackendInfo

    @abstractmethod
    def load(self) -> None:
        """Load LLM connection or model into memory."""
        pass

    @abstractmethod
    def generate(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResult:
        """Generate response given system and user prompts."""
        pass


class EmbedBackend(ABC):
    info: BackendInfo

    @abstractmethod
    def load(self) -> None:
        """Load embedding model assets."""
        pass

    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate normalized embedding vectors for texts."""
        pass
