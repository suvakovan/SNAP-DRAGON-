# LectureLens — Headline Verification Results

> **Important:** This file contains only measurements taken on the actual development machine.
> Claims are annotated with the exact method used to generate each number.

---

## 1. Device & Hardware Status

| Component | Value | Source |
| :--- | :--- | :--- |
| **Machine Architecture** | AMD64 (Intel64 Family 6 Model 190, 8 Cores) | `scripts/check_env.py` |
| **OS** | Windows 11 (10.0.26200) | `scripts/check_env.py` |
| **RAM** | 7.75 GB | `scripts/check_env.py` |
| **ONNX Runtime** | 1.30.0 ✅ | `scripts/check_env.py` |
| **QNNExecutionProvider** | ❌ NOT AVAILABLE on this machine | `scripts/check_env.py` |
| **Foundry Local (NPU LLM)** | ❌ NOT AVAILABLE on this machine | `scripts/check_env.py` |

> [!IMPORTANT]
> **NPU Acceleration Status:** `verified_npu = FALSE` on this development machine (Intel AMD64 laptop).
> The QNN Execution Provider and Foundry Local require a Qualcomm Snapdragon X Series SoC with HTP driver.
> All measurements below were taken on CPU fallback paths. NPU paths have been code-tested but not hardware-verified on this machine.

---

## 2. STT Backend Info (Verified at Runtime)

| Field | Value |
| :--- | :--- |
| `device` | **CPU** |
| `runtime` | `whisper-pytorch-cpu` (PyTorch Whisper `tiny` fallback) |
| `verified_npu` | **False** |
| `name` | `whisper-tiny` |
| **Reason for CPU** | `QNNExecutionProvider` not present; ONNX model files not found → PyTorch fallback activated |

---

## 3. LLM Backend Info (Verified at Runtime)

| Field | Value |
| :--- | :--- |
| `device` | **CPU** |
| `runtime` | `cpu-local-llm` (Ollama, model: `phi3:mini`) |
| `verified_npu` | **False** |
| `tokens_per_second` | **4.93 tok/sec** (measured, real inference) |
| `time_to_first_token` | **15.25 s** (measured) |
| `total_seconds` | **249.37 s** for full notes generation |
| **Reason for CPU** | Foundry Local not available; Ollama CPU path used |

---

## 4. STT WER Measurement

> [!NOTE]
> **Previous claim of WER = 0.0 was incorrect.** `scripts/consistency_check.py` was comparing a hardcoded string to itself (identical strings), which trivially yields WER = 0.0 and means nothing.

**Corrected measurement** — `checkpoint_sample.wav` (18.85s TTS-generated audio):

| Metric | Value | Method |
| :--- | :--- | :--- |
| **Reference** | TTS source script (human-typed, `checkpoint_sample_reference.txt`) | 40 words |
| **Hypothesis** | Actual Whisper-tiny CPU output (`actual_transcript.txt`) | 40 words |
| **WER** | **0.10 (10%)** | Levenshtein edit distance / reference word count |
| **Char Similarity** | **0.9894** | SequenceMatcher ratio |
| **Plausible?** | ✅ Yes — 10% WER is typical for Whisper-tiny on clean TTS speech |

**Reference text:**
> "Welcome to the LectureLens machine learning and natural language processing lecture. Today we will explore automatic speech recognition using neural networks and quantized NPU execution providers on the Snapdragon platform. We will analyze audio signals and generate detailed study notes."

**Actual STT output:**
> "Welcome to the lecture lens machine learning and natural language processing lecture. Today we will explore automatic speech recognition using neural networks and quantized NPU execution providers on snapdragon platforms. We will analyze audio signals and generate detailed study notes."

**Key differences** (4 word errors out of 40):
- "LectureLens" → "lecture lens" (split, 2 word errors)
- "the Snapdragon platform" → "snapdragon platforms" (1 substitution)

---

## 5. LLM Grounding Quality

> [!NOTE]
> **Previous claim of grounding = 1.0 was from the static fallback code path**, not a live LLM measurement.
> `scripts/quality_check.py` falls back to `mean_grounding = 1.0` when `backend.info.is_real` was `False`.

**Corrected description** of real grounding:  

The `quality_check.py` `evaluate_grounding()` function measures **lexical word overlap** between quiz answer text and the source transcript:
- It filters to content words (> 3 characters)
- Counts how many appear in the transcript word-set
- Reports the fraction (0.0–1.0)

**Sample size for the 1.0 claim:** 0 real LLM calls (the static path was triggered). The number should be treated as **unmeasured** until run on a Snapdragon NPU or Foundry-Local-enabled machine.

**Real quiz grounding spot-check** (from the actual Ollama phi3:mini pipeline run on `checkpoint_sample.wav`):

The session from `pipeline/session.py` run (`fa197e54`) produced:
- Summary bullets: "AI involves defining intelligence...", "Hexagon NPUs accelerate on-device AI..."
- Quiz: "What topic will be explored in today's lecture?" → Answer: "Snapdragon platform." (transcript: "...on snapdragon platforms..." ✅ grounded)
- Flashcard: "What is ASR?" → "Automatic speech recognition" (transcript: "automatic speech recognition using neural networks" ✅ grounded)
- Flashcard: "What is an NPU?" → "A Neural Processing Unit with optimized parameters..." (transcript: "quantized NPU execution providers" ✅ grounded)

**Approximate manual grounding on 3/3 spot-checked items: grounded.** However, sample size is too small for a statistical claim.

---

## 6. Test Suite Results

| Suite | Command | Result |
| :--- | :--- | :--- |
| Unit + Integration (24 tests) | `pytest` | ✅ **24/24 passed** |
| Offline socket guard | `python scripts/offline_check.py` | ✅ **0 external network calls** |
| Consistency / WER | `python scripts/consistency_check.py` | ✅ **WER=0.10, plausible** |
| No-simulation production guard | `tests/test_no_simulation_in_prod.py` | ✅ **5/5 passed** |

---

## 7. Summary Statement for Submission

```
STT:  device=CPU, runtime=whisper-pytorch-cpu, verified_npu=False
LLM:  device=CPU, runtime=cpu-local-llm (Ollama phi3:mini), verified_npu=False
WER (Whisper-tiny, TTS clean speech, 40 words): 0.10 (10%), plausible
LLM throughput (Ollama phi3:mini, CPU): 4.93 tok/sec, TTFT=15.25s
Grounding: spot-checked 3/3 outputs, all vocabulary-grounded in transcript
Tests: 24/24 passed, 0 external network calls in offline check
NPU status: QNNExecutionProvider=UNAVAILABLE (Intel AMD64 dev machine)
NPU code-path: implemented in stt_qnn.py + llm_foundry.py, requires Snapdragon X SoC
```

> [!WARNING]
> No NPU timing numbers are available from this machine. Any NPU speedup claims in the README benchmark table (`~42.5 tok/sec`, `RTF ~0.021`) were not generated on this machine and must be considered **projected / design-intent** until verified on Snapdragon X hardware.
