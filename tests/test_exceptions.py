"""Tests for custom exception hierarchy."""

import pytest
from lecturelens.exceptions import (
    LectureLensError, AudioError, AudioDeviceNotFoundError,
    TranscriptionError, NoteGenerationError, SchemaValidationError,
    SearchError, StorageError, SessionNotFoundError, ConfigurationError,
)


class TestExceptionHierarchy:
    def test_base_exception(self):
        with pytest.raises(LectureLensError):
            raise LectureLensError("base error")

    def test_audio_error_inherits(self):
        with pytest.raises(LectureLensError):
            raise AudioError("audio error")

    def test_device_not_found_inherits(self):
        with pytest.raises(AudioError):
            raise AudioDeviceNotFoundError("no mic")

    def test_transcription_error(self):
        with pytest.raises(LectureLensError):
            raise TranscriptionError("STT failed")

    def test_schema_validation_inherits(self):
        with pytest.raises(NoteGenerationError):
            raise SchemaValidationError("bad JSON")

    def test_session_not_found_inherits(self):
        with pytest.raises(StorageError):
            raise SessionNotFoundError("missing session")

    def test_config_error(self):
        with pytest.raises(LectureLensError):
            raise ConfigurationError("bad config")
