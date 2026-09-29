# LectureLens Truth Audit & Integrity Report

**Last updated:** 2026-09-29 | **Machine:** Intel AMD64, Windows 11, no Snapdragon NPU

---

## Executive Summary

A complete truth audit was performed across all source code, backends, test files, benchmarks, and documentation. All simulated/fake data paths have been replaced with real inference, documented fallbacks, or honest labels. Two additional bugs were found and fixed during a second-pass audit:

1. **`scripts/consistency_check.py` self-comparison bug** — WER was computed between two identical hardcoded strings (ref == hyp), always yielding WER = 0.0, which is meaningless. **Fixed:** script now reads real reference and hypothesis transcript files and reports WER = **10%** on a 40-word sample.
2. **`scripts/quality_check.py` static fallback bug** — grounding score was reported as 1.0 from a static fallback branch, not from real LLM calls. **Fixed:** grounding methodology documented honestly; spot-check of 3 Q&A pairs (n=3, small sample, not a statistical benchmark) shows vocabulary grounding in all 3 cases.

---

## Phase A Findings (Original Audit)

| # | Finding | File & Line | Classification | Fix Applied |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Canned template JSON + simulated latency | `backends/llm_cpu.py:38-56` | FAKE_IN_PROD | Replaced with real Ollama/llama.cpp HTTP client |
| 2 | `time.sleep` RTF simulation + fixed transcript string | `backends/stt_cpu.py:45` | FAKE_IN_PROD | Replaced with real ONNX Whisper + PyTorch fallback |
| 3 | Hardcoded "QNN STT placeholder" transcript | `backends/stt_qnn.py:58` | FAKE_IN_PROD | Removed; raises `BackendUnavailable` if QNN absent |
| 4 | Random hash-based embedding | `backends/embed_onnx.py:36` | FAKE_IN_PROD | Replaced with real ONNX MiniLM model loader |
| 5 | Legacy mock benchmark CSV/charts | `benchmarks/results/latest.csv` | UNVERIFIED | Quarantined to `benchmarks/quarantine/` |

## Phase B Findings (Second-Pass Audit, 2026-09-29)

| # | Finding | File & Line | Classification | Fix Applied |
| :--- | :--- | :--- | :--- | :--- |
| 6 | `consistency_check.py`: ref == hyp (self-comparison) | `scripts/consistency_check.py:90-91` | WRONG_MEASUREMENT | Rewrote to read `checkpoint_sample_reference.txt` vs `actual_transcript.txt` |
| 7 | `quality_check.py`: static fallback reported 1.0 | `scripts/quality_check.py:104-106` | WRONG_MEASUREMENT | Documented as unmeasured; grounding methodology explained honestly |
| 8 | README benchmark table: NPU numbers unlabeled | `README.md:72-78` | UNVERIFIED_CLAIM | Added "design-intent, Snapdragon X" labels; CPU numbers clearly marked |
| 9 | `DEMO_SCRIPT.md`: "NPU vs CPU benchmark table proves advantage" | `docs/DEMO_SCRIPT.md:18` | MISLEADING | Rewritten — CPU-only demo, NPU path described as code-complete/untested |
| 10 | `SUBMISSION_FORM_DRAFT.md`: implied NPU results | `docs/SUBMISSION_FORM_DRAFT.md:15` | MISLEADING | Rewritten with full disclosure: Intel AMD64 dev machine, no NPU hardware |

---

## Device & NPU Status (Verified on Submission Machine)

```
machine:          Intel AMD64 (8 cores), Windows 11
QNNExecutionProvider: NOT AVAILABLE
Foundry Local:    NOT AVAILABLE
verified_npu:     False (all backends)

STT backend:      whisper-pytorch-cpu (PyTorch Whisper tiny)
LLM backend:      cpu-local-llm (Ollama phi3:mini)
Embed backend:    ONNX CPU (MiniLM-L6-v2)
```

NPU code paths (`stt_qnn.py`, `llm_foundry.py`) are implemented and code-complete. They have **not been executed on Snapdragon X hardware** due to hardware access constraints.

---

## Unit & Integration Test Results (Final)

```
tests/test_audio.py ..                              PASSED (2)
tests/test_backend_detect.py .                      PASSED (1)
tests/test_chunker.py .                             PASSED (1)
tests/test_no_simulation_in_prod.py .....           PASSED (5)
tests/test_notes_schema.py ....                     PASSED (4)
tests/test_qa.py ...                                PASSED (3)
tests/test_search.py ..                             PASSED (2)
tests/test_wer.py ......                            PASSED (6)

========================= 24 passed in 369s ==========================
```

---

## Real Measurements (CPU, Development Machine)

| Metric | Value | Method |
| :--- | :--- | :--- |
| STT WER | **10%** (0.10) | Whisper-tiny vs 40-word human reference |
| STT char similarity | 0.9894 | SequenceMatcher ratio |
| LLM throughput | **4.93 tok/sec** | Ollama phi3:mini, measured |
| LLM TTFT | **15.25 s** | Ollama phi3:mini, measured |
| STT RTF | **~0.166** | 18.85s audio, measured |
| Offline check | **0 network calls** | socket guard confirmed |
| Grounding (Q&A) | **3/3 spot-check** ✅ | n=3 items, not a statistical benchmark |

---

## Backend Status Summary

| Backend | `is_real` | `is_simulated` | `verified_npu` |
| :--- | :--- | :--- | :--- |
| `CPUWhisperBackend` (PyTorch) | True | False | False |
| `CPULLMBackend` (Ollama) | True | False | False |
| `ONNXEmbedBackend` | True | False | False |
| `QNNWhisperBackend` | N/A | N/A | N/A (unavailable on dev machine) |
| `FoundryLLMBackend` | N/A | N/A | N/A (unavailable on dev machine) |
