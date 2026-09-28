# Engineering Decision Log (DECISIONS.md)

## ADR-001: Native Python ARM64 Environment Selection
- **Date:** 2026-09-28
- **Context:** Hardware acceleration on Snapdragon X requires native ARM64 Python execution to interface with Qualcomm QNN DLLs (`QnnHtp.dll`).
- **Decision:** Target Windows 11 ARM64 native Python 3.11/3.12 with fallback support for x86_64 CPU emulation environments.

## ADR-002: Modular Backend Abstract Interfaces
- **Date:** 2026-09-28
- **Context:** Heterogeneous laptop environments might lack specific NPU execution providers or runtime libraries.
- **Decision:** Implemented `STTBackend`, `LLMBackend`, and `EmbedBackend` abstract base classes. Hardware detection at runtime automatically selects NPU if verified, or CPU fallback without breaking application execution.

## ADR-003: Energy VAD and Windowed Audio Chunker
- **Date:** 2026-09-28
- **Context:** Long lecture recordings exceed single-pass Whisper context and consume excessive NPU cycles during silent pauses.
- **Decision:** Implemented an energy-based Voice Activity Detection filter and 30-second sliding chunker with 1-second overlap deduplication.

## ADR-004: Strict JSON Schema Validation and Repair Pipeline
- **Date:** 2026-09-28
- **Context:** Small local LLMs occasionally return markdown code blocks or minor syntax defects in JSON responses.
- **Decision:** Implemented regex backtick stripping, smart quote normalization, trailing comma repair, and Pydantic schema validation for quizzes and flashcards.
