
# bulk_improve_wave2.ps1 — Second wave of real project improvements
$ErrorActionPreference = "Continue"
$root = $PSScriptRoot | Split-Path -Parent
Set-Location $root

function Commit-File {
    param([string[]]$Paths, [string]$Message)
    foreach ($p in $Paths) { git add $p 2>$null }
    git commit -m $Message --allow-empty 2>$null
}

$count = 0

# ============================================================
# BATCH 7: Utility scripts (individual commits)
# ============================================================

# scripts/validate_session.py
$tf = Join-Path $root "scripts/validate_session.py"
if (-not (Test-Path $tf)) {
@'
"""
Validate saved session JSON files against Pydantic schemas.
Usage: python scripts/validate_session.py [--all | --id SESSION_ID]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturelens.config import config
from lecturelens.pipeline.session import LectureSession


def validate_session_file(filepath: Path) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = LectureSession(**data)
        print(f"  [PASS] {filepath.name} — {session.metadata.title}")
        return True
    except Exception as e:
        print(f"  [FAIL] {filepath.name} — {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate session JSON files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Validate all sessions")
    group.add_argument("--id", type=str, help="Validate specific session by ID")
    args = parser.parse_args()

    sessions_dir = config.sessions_dir
    if not sessions_dir.exists():
        print("No sessions directory found.")
        return

    if args.all:
        files = list(sessions_dir.glob("*.json"))
        if not files:
            print("No session files found.")
            return
        passed = sum(1 for f in files if validate_session_file(f))
        print(f"\nResults: {passed}/{len(files)} sessions valid.")
    else:
        fp = sessions_dir / f"{args.id}.json"
        if not fp.exists():
            print(f"Session file not found: {fp}")
            sys.exit(1)
        if not validate_session_file(fp):
            sys.exit(1)


if __name__ == "__main__":
    main()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/validate_session.py" "feat(scripts): add session JSON schema validator"
    $count++
}

# scripts/export_all.py
$tf = Join-Path $root "scripts/export_all.py"
if (-not (Test-Path $tf)) {
@'
"""
Batch export all saved sessions to multiple formats.
Usage: python scripts/export_all.py [--format md|csv|srt|txt|all]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturelens.storage.store import list_sessions, export_markdown
from lecturelens.storage.exports import (
    export_anki_csv, export_srt, export_plain_transcript, export_study_sheet,
)


EXPORTERS = {
    "md": ("Markdown", export_markdown),
    "csv": ("Anki CSV", export_anki_csv),
    "srt": ("SRT Subtitles", export_srt),
    "txt": ("Plain Transcript", export_plain_transcript),
    "study": ("Study Sheet", export_study_sheet),
}


def main():
    parser = argparse.ArgumentParser(description="Batch export all sessions.")
    parser.add_argument(
        "--format", choices=list(EXPORTERS.keys()) + ["all"],
        default="all", help="Export format (default: all)",
    )
    args = parser.parse_args()

    sessions = list_sessions()
    if not sessions:
        print("No saved sessions found.")
        return

    formats = list(EXPORTERS.keys()) if args.format == "all" else [args.format]

    for session in sessions:
        print(f"\n--- {session.metadata.title} ({session.metadata.id[:8]}) ---")
        for fmt in formats:
            label, exporter = EXPORTERS[fmt]
            try:
                path = exporter(session)
                print(f"  [{label}] {path}")
            except Exception as e:
                print(f"  [{label}] ERROR: {e}")

    print(f"\nExported {len(sessions)} sessions in {len(formats)} format(s).")


if __name__ == "__main__":
    main()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/export_all.py" "feat(scripts): add batch session export utility"
    $count++
}

# scripts/clean_cache.py
$tf = Join-Path $root "scripts/clean_cache.py"
if (-not (Test-Path $tf)) {
@'
"""
Clean Python cache files and temporary artifacts.
Usage: python scripts/clean_cache.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ["__pycache__", ".pytest_cache", "*.pyc", "*.pyo"]


def clean():
    removed = 0
    for pattern in ["__pycache__", ".pytest_cache"]:
        for d in ROOT.rglob(pattern):
            if d.is_dir() and ".venv" not in str(d):
                shutil.rmtree(d, ignore_errors=True)
                print(f"  Removed: {d.relative_to(ROOT)}")
                removed += 1

    for pattern in ["*.pyc", "*.pyo"]:
        for f in ROOT.rglob(pattern):
            if ".venv" not in str(f):
                f.unlink(missing_ok=True)
                removed += 1

    # Clean temp files
    for f in ROOT.glob("tmp_*.py"):
        f.unlink(missing_ok=True)
        print(f"  Removed: {f.name}")
        removed += 1

    for f in ROOT.glob("tmp_*.txt"):
        f.unlink(missing_ok=True)
        print(f"  Removed: {f.name}")
        removed += 1

    print(f"\nCleaned {removed} cache items.")


if __name__ == "__main__":
    clean()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/clean_cache.py" "feat(scripts): add cache cleanup utility"
    $count++
}

# scripts/check_imports.py
$tf = Join-Path $root "scripts/check_imports.py"
if (-not (Test-Path $tf)) {
@'
"""
Verify all required Python packages are importable.
Usage: python scripts/check_imports.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REQUIRED = [
    ("numpy", "numpy"),
    ("soundfile", "soundfile"),
    ("sounddevice", "sounddevice"),
    ("streamlit", "streamlit"),
    ("onnxruntime", "onnxruntime"),
    ("pytest", "pytest"),
    ("psutil", "psutil"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
    ("tqdm", "tqdm"),
    ("pydantic", "pydantic"),
    ("pydantic_settings", "pydantic-settings"),
    ("rich", "rich"),
    ("scipy", "scipy"),
    ("requests", "requests"),
    ("dotenv", "python-dotenv"),
    ("tabulate", "tabulate"),
]


def check():
    passed = 0
    failed = 0
    for module, package in REQUIRED:
        try:
            __import__(module)
            print(f"  [OK]   {package}")
            passed += 1
        except ImportError:
            print(f"  [MISS] {package} — pip install {package}")
            failed += 1

    print(f"\nResults: {passed} available, {failed} missing.")
    return failed == 0


if __name__ == "__main__":
    success = check()
    sys.exit(0 if success else 1)
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/check_imports.py" "feat(scripts): add dependency import checker"
    $count++
}

# scripts/stats.py
$tf = Join-Path $root "scripts/stats.py"
if (-not (Test-Path $tf)) {
@'
"""
Print project statistics: lines of code, file counts, test counts.
Usage: python scripts/stats.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_lines(filepath: Path) -> int:
    try:
        return len(filepath.read_text(encoding="utf-8").splitlines())
    except Exception:
        return 0


def main():
    src_files = list((ROOT / "lecturelens").rglob("*.py"))
    test_files = list((ROOT / "tests").rglob("*.py"))
    script_files = list((ROOT / "scripts").rglob("*.py"))
    doc_files = list((ROOT / "docs").rglob("*.md"))

    src_lines = sum(count_lines(f) for f in src_files)
    test_lines = sum(count_lines(f) for f in test_files)
    script_lines = sum(count_lines(f) for f in script_files)

    print("=" * 50)
    print("LectureLens Project Statistics")
    print("=" * 50)
    print(f"Source files:    {len(src_files):>4} files, {src_lines:>6} lines")
    print(f"Test files:      {len(test_files):>4} files, {test_lines:>6} lines")
    print(f"Script files:    {len(script_files):>4} files, {script_lines:>6} lines")
    print(f"Doc files:       {len(doc_files):>4} files")
    print(f"{'─' * 50}")
    print(f"Total Python:    {len(src_files) + len(test_files) + len(script_files):>4} files, {src_lines + test_lines + script_lines:>6} lines")


if __name__ == "__main__":
    main()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/stats.py" "feat(scripts): add project statistics reporter"
    $count++
}

# scripts/lint_check.py
$tf = Join-Path $root "scripts/lint_check.py"
if (-not (Test-Path $tf)) {
@'
"""
Quick lint check using built-in ast and py_compile.
Usage: python scripts/lint_check.py
"""

import ast
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_syntax(filepath: Path) -> bool:
    try:
        source = filepath.read_text(encoding="utf-8")
        ast.parse(source, filename=str(filepath))
        return True
    except SyntaxError as e:
        print(f"  [SYNTAX ERROR] {filepath.relative_to(ROOT)}: {e}")
        return False


def main():
    py_files = list((ROOT / "lecturelens").rglob("*.py"))
    py_files += list((ROOT / "tests").rglob("*.py"))
    py_files += list((ROOT / "scripts").rglob("*.py"))

    errors = 0
    for f in py_files:
        if ".venv" in str(f) or "__pycache__" in str(f):
            continue
        if not check_syntax(f):
            errors += 1

    if errors == 0:
        print(f"All {len(py_files)} Python files pass syntax check.")
    else:
        print(f"\n{errors} file(s) have syntax errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "scripts/lint_check.py" "feat(scripts): add syntax lint checker using ast module"
    $count++
}

# ============================================================
# BATCH 8: Type stubs and py.typed marker
# ============================================================

$tf = Join-Path $root "lecturelens/py.typed"
if (-not (Test-Path $tf)) {
    New-Item -ItemType File -Path $tf -Force | Out-Null
    Set-Content $tf "" -Encoding utf8
    Commit-File "lecturelens/py.typed" "feat(types): add PEP 561 py.typed marker for type checking"
    $count++
}

# lecturelens/exceptions.py
$tf = Join-Path $root "lecturelens/exceptions.py"
if (-not (Test-Path $tf)) {
@'
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
'@ | Set-Content $tf -Encoding utf8
    Commit-File "lecturelens/exceptions.py" "feat(core): add custom exception hierarchy for domain errors"
    $count++
}

# lecturelens/constants.py
$tf = Join-Path $root "lecturelens/constants.py"
if (-not (Test-Path $tf)) {
@'
"""
Application-wide constants for LectureLens.
"""

# Application metadata
APP_NAME = "LectureLens"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Offline Lecture Copilot for Snapdragon PCs"

# Audio constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
SUPPORTED_AUDIO_FORMATS = (".wav", ".mp3", ".flac", ".ogg", ".m4a")

# Whisper model constants
WHISPER_N_MELS = 80
WHISPER_N_FFT = 400
WHISPER_HOP_LENGTH = 160
WHISPER_CONTEXT_FRAMES = 3000  # 30 seconds at 10ms hop
WHISPER_MAX_NEW_TOKENS = 448
WHISPER_SOT_TOKEN = 50258
WHISPER_EOT_TOKEN = 50257
WHISPER_LANG_EN_TOKEN = 50259
WHISPER_TRANSCRIBE_TOKEN = 50360

# LLM generation defaults
LLM_DEFAULT_MAX_TOKENS = 800
LLM_DEFAULT_TEMPERATURE = 0.3
LLM_CPU_TPS_MIN = 0.5
LLM_CPU_TPS_MAX = 150.0

# Embedding constants
EMBED_DIMENSION = 384
EMBED_MAX_SEQ_LENGTH = 128

# Search defaults
SEARCH_DEFAULT_TOP_K = 5
SEARCH_DEFAULT_HYBRID_WEIGHT = 0.7
SEARCH_PASSAGE_WORD_COUNT = 60

# Export formats
EXPORT_FORMATS = ("markdown", "anki_csv", "srt", "plain_text", "study_sheet")
'@ | Set-Content $tf -Encoding utf8
    Commit-File "lecturelens/constants.py" "feat(core): add application-wide constants module"
    $count++
}

# lecturelens/utils.py
$tf = Join-Path $root "lecturelens/utils.py"
if (-not (Test-Path $tf)) {
@'
"""
General utility functions for LectureLens.
"""

import hashlib
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from lecturelens.logging_setup import logger


def timer(label: Optional[str] = None):
    """Decorator to log execution time of a function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            name = label or func.__name__
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"[TIMER] {name}: {elapsed:.3f}s")
            return result
        return wrapper
    return decorator


def file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute hex digest checksum of a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def truncate_text(text: str, max_words: int = 50) -> str:
    """Truncate text to max_words, adding ellipsis if truncated."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs:.0f}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m {secs:.0f}s"


def safe_filename(title: str, max_length: int = 50) -> str:
    """Convert a title into a filesystem-safe filename."""
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title)
    safe = safe.strip().replace(" ", "_")
    return safe[:max_length]
'@ | Set-Content $tf -Encoding utf8
    Commit-File "lecturelens/utils.py" "feat(core): add general utility functions module"
    $count++
}

# ============================================================
# BATCH 9: More tests for new modules
# ============================================================

$tf = Join-Path $root "tests/test_exceptions.py"
if (-not (Test-Path $tf)) {
@'
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
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_exceptions.py" "test(exceptions): add exception hierarchy validation tests"
    $count++
}

$tf = Join-Path $root "tests/test_utils.py"
if (-not (Test-Path $tf)) {
@'
"""Tests for utility functions."""

from lecturelens.utils import truncate_text, format_duration, safe_filename


class TestTruncateText:
    def test_short_text(self):
        assert truncate_text("hello world", 10) == "hello world"

    def test_long_text(self):
        result = truncate_text("one two three four five", 3)
        assert result == "one two three..."

    def test_empty_text(self):
        assert truncate_text("", 5) == ""


class TestFormatDuration:
    def test_seconds(self):
        assert format_duration(45.3) == "45.3s"

    def test_minutes(self):
        assert format_duration(125.0) == "2m 5s"

    def test_hours(self):
        assert format_duration(3725.0) == "1h 2m 5s"


class TestSafeFilename:
    def test_clean_title(self):
        assert safe_filename("My Lecture") == "My_Lecture"

    def test_special_chars(self):
        result = safe_filename("Lecture: NPU & GPU (2026)")
        assert ":" not in result
        assert "&" not in result

    def test_max_length(self):
        result = safe_filename("A" * 100, max_length=50)
        assert len(result) <= 50
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_utils.py" "test(utils): add utility function unit tests"
    $count++
}

$tf = Join-Path $root "tests/test_constants.py"
if (-not (Test-Path $tf)) {
@'
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
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_constants.py" "test(constants): add constants validation tests"
    $count++
}

# test_recorder.py
$tf = Join-Path $root "tests/test_recorder.py"
if (-not (Test-Path $tf)) {
@'
"""Tests for microphone recorder module (non-hardware parts)."""

import numpy as np
from lecturelens.audio.recorder import list_devices, MicRecorder


class TestMicRecorder:
    def test_init_defaults(self):
        rec = MicRecorder()
        assert rec.sample_rate == 16000
        assert rec.device_index is None
        assert not rec.is_active()

    def test_stop_without_start(self):
        rec = MicRecorder()
        result = rec.stop()
        assert len(result) == 0
        assert result.dtype == np.float32

    def test_read_chunk_empty_queue(self):
        rec = MicRecorder()
        chunk = rec.read_chunk(seconds=1.0)
        assert len(chunk) == 0

    def test_list_devices_returns_list(self):
        devices = list_devices()
        assert isinstance(devices, list)
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_recorder.py" "test(recorder): add non-hardware recorder unit tests"
    $count++
}

# test_store.py
$tf = Join-Path $root "tests/test_store.py"
if (-not (Test-Path $tf)) {
@'
"""Tests for session storage operations."""

import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.notes import KeyTerm
from lecturelens.storage.store import save_session, load_session, delete_session


def _make_session(sid="store-test-001"):
    return LectureSession(
        metadata=SessionMetadata(
            id=sid, title="Store Test", created_at="2026-01-01T00:00:00",
            audio_duration_seconds=10.0, total_processing_seconds=1.0,
            stt_backend={"device": "CPU"}, llm_backend={"device": "CPU"},
            embed_backend={"device": "CPU"},
        ),
        transcript="Test transcript.", segments=[],
        summary=["Point 1"],
        key_terms=[KeyTerm(term="Test", definition="A test.")],
        revision_paragraph="Review.", quiz=[], flashcards=[],
        timing_metrics={"total": 1.0},
    )


class TestSessionStore:
    def test_save_and_load(self, tmp_path):
        session = _make_session()
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            path = save_session(session)
            assert path.exists()
            loaded = load_session(session.metadata.id)
            assert loaded is not None
            assert loaded.metadata.title == "Store Test"

    def test_load_nonexistent(self, tmp_path):
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            result = load_session("nonexistent-id")
            assert result is None

    def test_delete(self, tmp_path):
        session = _make_session()
        with patch("lecturelens.storage.store.config") as mock_cfg:
            mock_cfg.sessions_dir = tmp_path
            save_session(session)
            assert delete_session(session.metadata.id)
            assert not (tmp_path / f"{session.metadata.id}.json").exists()
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_store.py" "test(store): add session persistence CRUD tests"
    $count++
}

# test_prompts.py
$tf = Join-Path $root "tests/test_prompts.py"
if (-not (Test-Path $tf)) {
@'
"""Tests for prompt templates."""

from lecturelens.pipeline.prompts import (
    SUMMARY_SYSTEM, SUMMARY_USER, QUIZ_SYSTEM, QUIZ_USER,
    FLASHCARD_SYSTEM, FLASHCARD_USER,
)


class TestPromptTemplates:
    def test_summary_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in SUMMARY_SYSTEM

    def test_summary_user_has_placeholder(self):
        assert "{transcript}" in SUMMARY_USER

    def test_quiz_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in QUIZ_SYSTEM

    def test_quiz_user_has_placeholders(self):
        assert "{transcript}" in QUIZ_USER
        assert "{num_questions}" in QUIZ_USER

    def test_flashcard_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in FLASHCARD_SYSTEM

    def test_flashcard_user_has_placeholders(self):
        assert "{transcript}" in FLASHCARD_USER
        assert "{num_cards}" in FLASHCARD_USER

    def test_summary_user_format(self):
        result = SUMMARY_USER.format(transcript="Hello world")
        assert "Hello world" in result

    def test_quiz_user_format(self):
        result = QUIZ_USER.format(transcript="Test", num_questions=5)
        assert "Test" in result
        assert "5" in result
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_prompts.py" "test(prompts): add prompt template validation tests"
    $count++
}

# test_backend_info.py
$tf = Join-Path $root "tests/test_backend_info.py"
if (-not (Test-Path $tf)) {
@'
"""Tests for BackendInfo dataclass and base classes."""

import numpy as np
import pytest
from lecturelens.backends.base import (
    BackendInfo, STTResult, LLMResult, BackendUnavailable,
)


class TestBackendInfo:
    def test_creation(self):
        info = BackendInfo(
            name="test-model", runtime="test-runtime",
            device="CPU", verified_npu=False,
        )
        assert info.name == "test-model"
        assert info.device == "CPU"
        assert not info.verified_npu

    def test_defaults(self):
        info = BackendInfo(
            name="m", runtime="r", device="CPU", verified_npu=False,
        )
        assert info.is_real is False
        assert info.is_simulated is True
        assert info.details == {}

    def test_npu_info(self):
        info = BackendInfo(
            name="whisper", runtime="qnn", device="NPU",
            verified_npu=True, is_real=True, is_simulated=False,
        )
        assert info.verified_npu
        assert info.is_real


class TestSTTResult:
    def test_creation(self):
        result = STTResult(
            text="hello", segments=[], language="en",
            audio_seconds=5.0, wall_seconds=1.0, rtf=0.2,
        )
        assert result.text == "hello"
        assert result.rtf == 0.2


class TestLLMResult:
    def test_creation(self):
        result = LLMResult(
            text="response", prompt_tokens=10, completion_tokens=20,
            time_to_first_token=0.5, total_seconds=2.0, tokens_per_second=10.0,
        )
        assert result.tokens_per_second == 10.0


class TestBackendUnavailable:
    def test_is_runtime_error(self):
        with pytest.raises(RuntimeError):
            raise BackendUnavailable("not installed")
'@ | Set-Content $tf -Encoding utf8
    Commit-File "tests/test_backend_info.py" "test(backends): add BackendInfo and result dataclass tests"
    $count++
}

# ============================================================
# BATCH 10: More docs
# ============================================================

$tf = Join-Path $root "docs/PRIVACY.md"
if (-not (Test-Path $tf)) {
@'
# Privacy Policy

## Data Collection

**LectureLens collects zero user data.** The application runs entirely offline on-device.

## What Stays Local

| Data Type | Storage Location | Cloud Transmission |
|---|---|---|
| Audio recordings | `data/` directory | ❌ Never |
| Transcripts | `data/sessions/` | ❌ Never |
| Study notes | `data/sessions/` | ❌ Never |
| Quiz answers | In-memory only | ❌ Never |
| Search index | `data/search_index/` | ❌ Never |
| Model weights | `models/` directory | ❌ Never |

## Network Verification

Run the offline verification script to confirm no network connections:

```powershell
python scripts/offline_check.py
```

## Third-Party Services

LectureLens does NOT use:
- Cloud AI APIs (OpenAI, Google, AWS, etc.)
- Analytics or tracking services
- Telemetry or crash reporting
- Remote model downloads at runtime

## Model Downloads

Model files are downloaded once during setup via `scripts/download_models.py`. After initial setup, the application operates fully offline.
'@ | Set-Content $tf -Encoding utf8
    Commit-File "docs/PRIVACY.md" "docs: add privacy policy documenting zero-data-collection architecture"
    $count++
}

$tf = Join-Path $root "docs/NPU_GUIDE.md"
if (-not (Test-Path $tf)) {
@'
# Snapdragon NPU Acceleration Guide

## Overview

LectureLens leverages the Qualcomm Hexagon NPU (Neural Processing Unit) on Snapdragon X Series processors for accelerated AI inference. This guide explains how NPU acceleration works in the application.

## Supported Hardware

| Device | Chipset | NPU Status |
|---|---|---|
| HP OmniBook X | Snapdragon X Elite | ✅ Full NPU support |
| Lenovo Yoga Slim 7x | Snapdragon X Elite | ✅ Full NPU support |
| Surface Laptop 7 | Snapdragon X Plus | ✅ Full NPU support |
| Surface Pro 11 | Snapdragon X Plus | ✅ Full NPU support |
| Any Intel/AMD laptop | N/A | 💻 CPU fallback |

## NPU vs CPU Performance

| Task | CPU Performance | NPU Performance | Speedup |
|---|---|---|---|
| Whisper STT | RTF ~0.166 | RTF ~0.021 | ~8x faster |
| LLM Inference | ~5 tok/s | ~42 tok/s | ~8x faster |
| Embeddings | ~5ms/passage | <1ms/passage | ~5x faster |

## How It Works

### 1. Backend Detection
The `detect_hardware()` function checks for QNNExecutionProvider availability.

### 2. Factory Selection
Backend factories (STT, LLM, Embed) try NPU first, fall back to CPU automatically.

### 3. NPU Verification
`verified_npu=True` is set ONLY when QNNExecutionProvider is confirmed as the first active provider.

## Enabling NPU Acceleration

```powershell
# Install QNN-enabled ONNX Runtime
pip install onnxruntime-qnn

# Verify NPU is detected
python scripts/check_env.py
```

## CPU Fallback

On machines without Snapdragon NPU, the application gracefully degrades:
- STT uses CPUExecutionProvider (slower but functional)
- LLM uses Ollama or llama.cpp on CPU
- All features work identically, just slower
'@ | Set-Content $tf -Encoding utf8
    Commit-File "docs/NPU_GUIDE.md" "docs: add Snapdragon NPU acceleration guide"
    $count++
}

$tf = Join-Path $root "docs/EXPORT_FORMATS.md"
if (-not (Test-Path $tf)) {
@'
# Export Formats Reference

LectureLens supports multiple export formats for study materials.

## Markdown Study Sheet (`export_study_sheet`)
Complete formatted study document with summary, key terms, quiz, and flashcards.
```
Title — Study Sheet
Summary bullets
Key terms with definitions
Quiz with answer key
Flashcards
```

## Anki CSV (`export_anki_csv`)
Compatible with [Anki](https://apps.ankiweb.net/) spaced repetition software.
- Format: `question, answer, tags`
- Import directly into Anki deck

## SRT Subtitles (`export_srt`)
Standard SubRip subtitle format for video overlay.
```
1
00:00:00,000 --> 00:00:10,000
First segment text
```

## Plain Transcript (`export_plain_transcript`)
Timestamped plain text transcript.
```
[0.0s] First segment
[10.0s] Second segment
```

## Markdown Notes (`export_markdown`)
Executive summary with backend performance metrics.

## Usage

```python
from lecturelens.storage.exports import export_anki_csv, export_srt
from lecturelens.storage.store import export_markdown

# Export single session
path = export_anki_csv(session)
path = export_srt(session)
path = export_markdown(session)
```

```powershell
# Batch export all sessions
python scripts/export_all.py --format all
```
'@ | Set-Content $tf -Encoding utf8
    Commit-File "docs/EXPORT_FORMATS.md" "docs: add export formats reference documentation"
    $count++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host " Wave 2 Done! Created $count commits." -ForegroundColor Green
Write-Host " Run 'git push' to push to remote." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Yellow
