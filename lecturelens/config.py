"""
Configuration management for LectureLens using Pydantic Settings.
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    app_name: str = "LectureLens"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")
    sessions_dir: Path = Path("./data/sessions")
    models_dir: Path = Path("./models")
    logs_dir: Path = Path("./logs")

    # Audio Settings
    sample_rate: int = 16000
    chunk_seconds: int = 30
    overlap_seconds: float = 1.0
    vad_threshold: float = 0.01

    # Speech to Text
    stt_backend_preference: str = "auto"  # auto, npu, cpu
    stt_model_name: str = "whisper-base-en"
    stt_language: str = "en"

    # LLM
    llm_backend_preference: str = "auto"  # auto, npu, cpu
    foundry_endpoint: str = "http://localhost:5272/v1"
    ollama_endpoint: str = "http://localhost:11434"
    llm_model_name: str = "phi-3-mini"
    llm_max_tokens: int = 800
    llm_temperature: float = 0.3

    # Embeddings
    embed_backend_preference: str = "auto"  # auto, npu, cpu
    embed_model_name: str = "all-MiniLM-L6-v2"

    def ensure_directories(self) -> None:
        """Create necessary directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


config = Settings()
config.ensure_directories()
