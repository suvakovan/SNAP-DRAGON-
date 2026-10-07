"""Tests for application constants."""

from lecturelens.constants import (
    APP_NAME, APP_VERSION, DEFAULT_SAMPLE_RATE,
    SUPPORTED_AUDIO_FORMATS, WHISPER_SOT_TOKEN,
    EMBED_DIMENSION, SEARCH_DEFAULT_TOP_K, EXPORT_FORMATS,
)


class TestConstants:
    def test_app_name(self):
        assert APP_NAME == "LectureLens"

    def test_sample_rate(self):
        assert DEFAULT_SAMPLE_RATE == 16000

    def test_supported_formats(self):
        assert ".wav" in SUPPORTED_AUDIO_FORMATS
        assert ".mp3" in SUPPORTED_AUDIO_FORMATS

    def test_whisper_tokens(self):
        assert WHISPER_SOT_TOKEN == 50258

    def test_embed_dimension(self):
        assert EMBED_DIMENSION == 384

    def test_search_defaults(self):
        assert SEARCH_DEFAULT_TOP_K == 5

    def test_export_formats(self):
        assert "markdown" in EXPORT_FORMATS
        assert "srt" in EXPORT_FORMATS
