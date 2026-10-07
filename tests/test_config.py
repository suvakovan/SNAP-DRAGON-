"""Tests for configuration management."""

from lecturelens.config import Settings


class TestConfig:
    def test_default_sample_rate(self):
        s = Settings()
        assert s.sample_rate == 16000

    def test_default_chunk_seconds(self):
        s = Settings()
        assert s.chunk_seconds == 30

    def test_default_stt_language(self):
        s = Settings()
        assert s.stt_language == "en"

    def test_default_log_level(self):
        s = Settings()
        assert s.log_level == "INFO"

    def test_app_name(self):
        s = Settings()
        assert s.app_name == "LectureLens"

    def test_backend_preferences_default_auto(self):
        s = Settings()
        assert s.stt_backend_preference == "auto"
        assert s.llm_backend_preference == "auto"
        assert s.embed_backend_preference == "auto"
