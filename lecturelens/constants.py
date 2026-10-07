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
