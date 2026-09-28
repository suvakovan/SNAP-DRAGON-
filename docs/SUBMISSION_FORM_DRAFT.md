# Unstop Challenge Submission Draft - LectureLens

## 1. Project Title
**LectureLens: Fully Offline Lecture Copilot for Snapdragon PCs**

## 2. One-Line Pitch
An offline lecture copilot for Snapdragon X laptops that converts speech to transcripts, summaries, quizzes, and search on-device with NPU acceleration.

## 3. Problem Statement & Target User
Engineering students often attend fast-paced lectures with poor connectivity and do not want private class audio sent to cloud servers. Cloud solutions introduce latency, high subscription fees, and privacy concerns.

<!-- INSERT: quote or survey result from real students -->

## 4. Solution Overview
LectureLens processes lecture audio 100% on-device using Qualcomm AI Hub models and Microsoft Foundry Local endpoints. It generates executive bullet summaries, key term glossaries, active recall flashcards, and interactive quizzes, while providing cross-lecture semantic search.

## 5. Technology Stack & Hardware Acceleration
- **Speech-to-Text:** Qualcomm AI Hub / ONNX Runtime with QNN HTP Execution Provider (CPU fallback)
- **Local LLM:** Microsoft Foundry Local NPU-targeted instruct variant / Local CPU LLM fallback
- **Embeddings & Search:** ONNX MiniLM vector embeddings + BM25 hybrid similarity index
- **UI:** Streamlit Web UI

## 6. Offline Guarantee
Verified via `scripts/offline_check.py` socket guard with 0 external network requests during full pipeline execution.
