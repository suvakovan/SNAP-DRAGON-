# LectureLens Final Engineering & QA Report

**Date:** 2026-09-29 | **Status:** Frozen for submission

---

## Executive Summary

LectureLens is a fully offline lecture copilot, built and CPU-verified on an Intel AMD64 development machine (Windows 11). The Snapdragon X / NPU code paths are implemented and code-complete but have not been executed on Snapdragon hardware due to access constraints before the submission deadline.

- **Unit Tests:** 24/24 passed (`pytest tests/`)
- **Offline Security Check:** PASS — 0 network calls (`scripts/offline_check.py`)
- **STT WER:** 10% (Whisper-tiny vs 40-word human reference — plausible)
- **LLM Speed:** 4.93 tok/sec (Ollama phi3:mini, CPU — real measurement)
- **Device (all backends):** `verified_npu = False` on development machine
- **NPU code paths:** Code-complete, not yet run on Snapdragon X hardware

---

## What Works & Hardware Fallback Status

1. **Audio Layer:** Preprocessing (mono conversion, 16 kHz resample, peak normalization), energy VAD, sliding window chunker with 1s overlap deduplication.
2. **STT Pipeline (CPU):** PyTorch Whisper-tiny fallback, RTF ~0.166, WER 10% on clean TTS speech.
3. **STT Pipeline (NPU, code-complete):** `backends/stt_qnn.py` wraps ONNX Runtime + QNNExecutionProvider. Raises `BackendUnavailable` cleanly on non-Snapdragon hardware.
4. **LLM Engine (CPU):** Ollama phi3:mini, 4.93 tok/sec, full notes + quiz + flashcard generation working end-to-end.
5. **LLM Engine (NPU, code-complete):** `backends/llm_foundry.py` wraps Foundry Local `/v1/chat/completions`. Raises `BackendUnavailable` cleanly when endpoint is unavailable.
6. **JSON Schema Repair:** Clean parsing, backtick removal, quote normalization, Pydantic validation for quizzes and flashcards.
7. **Cross-Lecture Search:** Hybrid vector embeddings (MiniLM) and BM25 search.
8. **Streamlit UI:** Responsive 8-tab app, hardware status card in sidebar, offline indicator badge, auto-loads latest session.

---

## Two Bugs Found & Fixed During Final Audit

### Bug 1: `consistency_check.py` self-comparison
- **Was:** `ref == hyp` (identical hardcoded strings) → WER = 0.0 by construction, meaningless.
- **Fix:** Script now reads `benchmarks/inputs/checkpoint_sample_reference.txt` (human reference) and `actual_transcript.txt` (real STT output).
- **Real WER:** **10%** (4 errors in 40 words — Whisper split "LectureLens" into "lecture lens", minor plural variation).

### Bug 2: `quality_check.py` static fallback
- **Was:** Fell into static branch returning `mean_grounding = 1.0` with 0 real LLM calls.
- **Fix:** Grounding methodology documented clearly. Real spot-check: 3/3 Q&A pairs from Ollama phi3:mini run are vocabulary-grounded in the transcript. Sample size (n=3) is too small for a statistical claim; labeled as a spot-check.

---

## Remaining Manual Steps for Human Submission

1. **Record Demo Video:** Follow `docs/DEMO_SCRIPT.md` — expected ~90 seconds.
2. **Submit Form:** Use `docs/SUBMISSION_FORM_DRAFT.md` as the source for the Unstop portal.
3. **Note for judges:** All NPU/Snapdragon claims in the codebase describe implemented code paths, not hardware-verified results. See `docs/HEADLINE_RESULTS.md` for full measurement transparency.
