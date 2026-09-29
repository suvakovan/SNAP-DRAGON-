# Unstop Challenge Submission Draft - LectureLens

## 1. Project Title
**LectureLens: Fully Offline Lecture Copilot — Designed for Snapdragon X PCs**

## 2. One-Line Pitch
An offline lecture copilot that converts speech to transcripts, summaries, quizzes, and semantic search entirely on-device — built and CPU-verified with an NPU/QNN code path ready for Snapdragon X hardware.

## 3. Problem Statement & Target User
Engineering students often attend fast-paced lectures with poor connectivity and do not want private class audio sent to cloud servers. Cloud solutions introduce latency, high subscription fees, and privacy concerns.

## 4. Solution Overview
LectureLens processes lecture audio 100% locally with no external API calls. It generates executive bullet summaries, key term glossaries, active recall flashcards, and interactive quizzes, while providing cross-lecture semantic search. All components run on-device with a privacy-first design.

## 5. Technology Stack & Hardware Acceleration

- **Speech-to-Text:** ONNX Runtime Whisper with Qualcomm QNN HTP Execution Provider code path (`backends/stt_qnn.py`). Falls back to PyTorch Whisper on CPU when QNN provider is unavailable.
- **Local LLM:** Microsoft Foundry Local NPU-targeted interface (`backends/llm_foundry.py`) with Ollama/llama.cpp CPU fallback (`backends/llm_cpu.py`).
- **Embeddings & Search:** ONNX MiniLM vector embeddings + BM25 hybrid similarity index.
- **UI:** Streamlit Web UI with hardware backend status display.

## 6. How Snapdragon / NPU is Used

> **Honest status (required disclosure):**
>
> Design and development were performed on an Intel AMD64 development machine (Windows 11, no Snapdragon SoC). The `QNNExecutionProvider` was not available during development, and **all reported performance numbers are from CPU fallback paths only** (`verified_npu = False`).
>
> The Snapdragon/NPU code paths are **implemented and code-complete**:
> - `lecturelens/backends/stt_qnn.py` — wraps `onnxruntime.InferenceSession` with `QNNExecutionProvider` and an ONNX Whisper model from Qualcomm AI Hub. Sets `verified_npu=True` only when the provider is confirmed active.
> - `lecturelens/backends/llm_foundry.py` — wraps the Microsoft Foundry Local `/v1/chat/completions` endpoint and sets `verified_npu=True` only when the endpoint is alive.
> - The `BackendInfo.verified_npu` flag propagates through the full pipeline and is displayed in the Streamlit UI sidebar and stored in session metadata.
>
> **These paths have not been executed or benchmarked on Snapdragon X hardware** due to hardware access constraints before the submission deadline. NPU speedup numbers quoted in the README benchmark table (RTF ~0.021, ~42.5 tok/sec) are design-intent projections based on published Qualcomm AI Hub benchmarks for Whisper-base and Phi-3-mini, not measurements from this machine.

## 7. Offline Guarantee
Verified via `scripts/offline_check.py` socket guard: **0 external network requests** during full pipeline execution (STT + LLM + embeddings + search). All model weights are stored locally; Ollama runs fully offline.

## 8. Measured CPU Performance (Development Machine)
- **STT:** Whisper-tiny via PyTorch CPU — RTF ~0.166 (measured on 18.85s audio)
- **STT WER:** 10% on 40-word TTS-generated reference (plausible for Whisper-tiny, clean speech)
- **LLM:** phi3:mini via Ollama CPU — 4.93 tok/sec, TTFT=15.25s
- **Tests:** 24/24 pytest unit+integration tests passing
- **Device:** `verified_npu = False` on development machine
