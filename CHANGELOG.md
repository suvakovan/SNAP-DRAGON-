# Changelog

All notable changes to LectureLens will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-07

### Added
- Core audio capture pipeline with microphone recording and file upload
- Energy-based Voice Activity Detection (VAD) with configurable thresholds
- Audio chunker with overlap deduplication and low-energy boundary cuts
- CPU Whisper STT backend via ONNX Runtime (CPUExecutionProvider)
- QNN Whisper STT backend for Snapdragon NPU acceleration (QNNExecutionProvider)
- LLM-powered lecture notes generation with schema-validated JSON output
- Interactive multiple-choice quiz generation with Pydantic validation
- Active recall flashcard generation
- Hybrid semantic search (vector + BM25) across lecture sessions
- Grounded Q&A pipeline with citation tracking
- Streamlit web UI with iQOO Cyber Yellow & Obsidian Black theme
- Session persistence with JSON storage
- Export formats: Markdown, Anki CSV, SRT subtitles, plain transcript
- Hardware detection for Qualcomm QNN, Foundry Local, and audio devices
- Comprehensive benchmark harness with CPU vs NPU comparison
- Offline verification guard script
- Full test suite with unit and integration tests

### Security
- Zero cloud API dependency â€” fully offline architecture
- No telemetry or data collection
- Local-only session storage
