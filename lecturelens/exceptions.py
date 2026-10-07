"""
Custom exception hierarchy for LectureLens.

All domain-specific exceptions inherit from LectureLensError
to allow broad catch patterns at the application boundary.
"""


class LectureLensError(Exception):
    """Base exception for all LectureLens errors."""
    pass


class AudioError(LectureLensError):
    """Raised when audio capture, loading, or preprocessing fails."""
    pass


class AudioDeviceNotFoundError(AudioError):
    """Raised when no audio input device is available."""
    pass


class AudioFormatError(AudioError):
    """Raised when audio file format is unsupported or corrupted."""
    pass


class TranscriptionError(LectureLensError):
    """Raised when speech-to-text transcription fails."""
    pass


class NoteGenerationError(LectureLensError):
    """Raised when LLM note/quiz/flashcard generation fails."""
    pass


class SchemaValidationError(NoteGenerationError):
    """Raised when LLM output fails Pydantic schema validation."""
    pass


class SearchError(LectureLensError):
    """Raised when search indexing or querying fails."""
    pass


class StorageError(LectureLensError):
    """Raised when session save/load/export operations fail."""
    pass


class SessionNotFoundError(StorageError):
    """Raised when a requested session ID does not exist."""
    pass


class ConfigurationError(LectureLensError):
    """Raised when configuration is invalid or missing."""
    pass
