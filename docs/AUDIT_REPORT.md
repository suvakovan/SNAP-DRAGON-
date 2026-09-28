# LectureLens Truth Audit & Integrity Report

## Executive Summary

During Phase A (Truth Audit), all source code, backends, test files, and benchmarks were audited for simulated/fake data, hard-coded metrics, and unverified NPU claims.

Key actions taken:
- Quarantined legacy mock benchmarks (`benchmarks/quarantine/`).
- Removed `time.sleep` and canned string outputs from production STT and LLM backends.
- Replaced mock CPU LLM backend with real Ollama / llama.cpp HTTP streaming client with plausibility guards.
- Replaced hash-based embed backend with real ONNX model loader; isolated deterministic hash vectors to `DeterministicEmbedBackend` (test-only).
- Updated QNN STT backend to set `verified_npu=False` and raise `BackendUnavailable` if QNN EP is absent.
- Enforced strict `BackendUnavailable` exception propagation in factories so no simulated backend can be returned in production mode.
- Created `tests/test_no_simulation_in_prod.py` to prevent future regressions.

---

## 🔍 Audit Findings Table

| # | Finding Description | File & Line | Classification | Action / Fix Applied |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Canned template JSON output & simulated latency | `lecturelens/backends/llm_cpu.py:38-56` | `FAKE_IN_PRODUCTION_PATH` | Replaced with real Ollama / llama.cpp HTTP client with TPS plausibility guard (0.5–150 tok/s). |
| 2 | `time.sleep` RTF simulation and fixed string transcript | `lecturelens/backends/stt_cpu.py:45` | `FAKE_IN_PRODUCTION_PATH` | Replaced with real ONNX Whisper model loader & greedy decode loop. Raises `BackendUnavailable` if model files absent. |
| 3 | Hardcoded string transcript "QNN STT placeholder" | `lecturelens/backends/stt_qnn.py:58` | `FAKE_IN_PRODUCTION_PATH` | Removed placeholder string; updated QNN session checker to set `verified_npu=False` and raise `BackendUnavailable` if QNN provider missing. |
| 4 | Random hash-based embedding generation | `lecturelens/backends/embed_onnx.py:36` | `FAKE_IN_PRODUCTION_PATH` | Replaced with real ONNX model loader (`all-MiniLM-L6-v2`). Moved hash vectors to `DeterministicEmbedBackend` (test-only). |
| 5 | Legacy mock benchmark results & charts | `benchmarks/results/latest.csv` | `UNVERIFIED_CLAIM` | Quarantined to `benchmarks/quarantine/`. Added `.gitignore` rule. |
| 6 | Synthetic audio array in offline guard check | `scripts/offline_check.py:65` | `TEST_ONLY` | Acceptable test fixture for network isolation guard verification. |
| 7 | Synthetic audio in Streamlit demo toggle | `lecturelens/ui/app.py:123` | `DEMO_MODE` | Acceptable demo feature; clearly labeled in UI sidebar as Demo Mode. |

---

## 🧪 Unit & Integrity Test Results

```
tests/test_audio.py::test_preprocess_audio PASSED
tests/test_audio.py::test_vad_detects_speech_bursts PASSED
tests/test_backend_detect.py::test_detect_hardware_structure PASSED
tests/test_chunker.py::test_chunker_coverage_and_overlap PASSED
tests/test_no_simulation_in_prod.py::test_stt_factory_does_not_return_simulated PASSED
tests/test_no_simulation_in_prod.py::test_llm_factory_does_not_return_simulated PASSED
tests/test_no_simulation_in_prod.py::test_embed_factory_does_not_return_simulated PASSED
tests/test_no_simulation_in_prod.py::test_determinist_embed_is_flagged_simulated PASSED
tests/test_no_simulation_in_prod.py::test_backend_info_fields_exist PASSED
tests/test_notes_schema.py::test_clean_and_parse_json_valid PASSED
tests/test_notes_schema.py::test_clean_and_parse_json_repair_trailing_comma PASSED
tests/test_notes_schema.py::test_quiz_question_validation PASSED
tests/test_notes_schema.py::test_generate_full_notes_end_to_end PASSED
tests/test_search.py::test_chunk_transcript_into_passages PASSED
tests/test_search.py::test_search_index_top_k PASSED

============================= 15 passed in 0.22s =============================
```

---

## 📋 Status of Backends

- **`STTBackend` (`QNNWhisperBackend` & `CPUWhisperBackend`):**
  - `is_real=True`, `is_simulated=False` when ONNX Whisper model files exist under `models/whisper-base-en/`.
  - Raises `BackendUnavailable` when model files are missing.
- **`LLMBackend` (`FoundryLLMBackend` & `CPULLMBackend`):**
  - `is_real=True`, `is_simulated=False` when connected to live Foundry Local or local Ollama / llama.cpp engine.
  - Raises `BackendUnavailable` when no server is running.
- **`EmbedBackend` (`ONNXEmbedBackend`):**
  - `is_real=True`, `is_simulated=False` when model exists under `models/all-MiniLM-L6-v2/`.
  - `DeterministicEmbedBackend` is strictly marked `is_simulated=True` and used only in unit tests.
