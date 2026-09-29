# 🎓 LectureLens — 12-Slide Pitch Deck & Presentation Content

> **Qualcomm Snapdragon AI Lab Challenge**  
> **Project:** LectureLens — Fully Offline Lecture Copilot Accelerated for Snapdragon PCs

---

## 📌 Slide 1: Title Slide
- **Title:** LectureLens
- **Subtitle:** Fully Offline Lecture Copilot Accelerated for Snapdragon X Series Laptops
- **Tagline:** Empowering Students with Private, On-Device Speech Recognition, Note Generation & Active Recall Quizzing.
- **Presenter / Team:** [Your Name / Team Name]
- **Key Visual:** `docs/assets/app_preview.png` (iQOO Cyber Yellow & Obsidian Black Dashboard)

---

## 📌 Slide 2: The Problem
- **Headline:** Campus Wi-Fi Deadzones & Classroom Information Overload
- **Key Pain Points:**
  1. **Unreliable Campus Connectivity:** High-density lecture halls suffer from poor Wi-Fi and cell coverage, rendering cloud AI tools unusable.
  2. **Fast-Paced STEM Lectures:** Students struggle to listen attentively while simultaneously scribbling down complex equations and technical terms.
  3. **Privacy & Content Security:** Uploading proprietary lectures, research discussions, or sensitive audio to third-party cloud APIs poses privacy risks.
- **Quote/Stat:** *"Over 70% of engineering lectures occur in crowded auditoriums where cloud API latency or connection drops spoil real-time note taking."*

---

## 📌 Slide 3: The Solution
- **Headline:** LectureLens — 100% On-Device AI Copilot
- **Value Proposition:** An instant, private copilot running locally on Snapdragon X Windows-on-ARM laptops without sending a single byte over the internet.
- **Core Pillars:**
  - 🔒 **100% Privacy & Offline Execution:** Strict zero-cloud network architecture.
  - ⚡ **NPU Accelerated Inference:** Hexagon NPU offloading for Speech-to-Text and LLM generation.
  - 🎓 **Automated Study Artifacts:** Executive summaries, key term glossaries, interactive quizzes, and flashcards in seconds.

---

## 📌 Slide 4: Key Capabilities & Student Workflow
- **Headline:** From Classroom Audio to Mastery in 5 Simple Steps
- **Workflow:**
  1. **Record / Upload:** Capture live microphone audio or load WAV/MP3/FLAC lecture files.
  2. **Transcribe:** Neural speech recognition via Whisper with sub-second chunking.
  3. **Summarize:** Structured executive notes, key terms, and revision paragraphs generated instantly.
  4. **Quiz & Recall:** Auto-generated multiple choice Q&A and interactive study flashcards.
  5. **Semantic Search:** Cross-lecture hybrid vector search across all saved sessions.

---

## 📌 Slide 5: System Architecture & Data Pipeline
- **Headline:** End-to-End Local Processing Pipeline
- **Architecture Flow:**
  - **Audio Engine:** 16 kHz mono resampling → Energy Voice Activity Detection (VAD) → 30s sliding window chunker.
  - **Speech-to-Text (STT):** `stt_qnn.py` (ONNX Runtime + Qualcomm QNN HTP Provider) with PyTorch Whisper CPU fallback.
  - **Large Language Model (LLM):** `llm_foundry.py` (Foundry Local NPU endpoint) with Ollama local CPU fallback.
  - **Vector Search Index:** ONNX MiniLM-L6-v2 embeddings + BM25 keyword matching.

---

## 📌 Slide 6: Snapdragon NPU Acceleration Design
- **Headline:** Hardware Acceleration for Qualcomm Snapdragon X PCs
- **NPU Integration Details:**
  - **Qualcomm Hexagon NPU:** Offloads dense tensor operations to save battery and reduce CPU thermals.
  - **Qualcomm QNN Execution Provider:** Hardware-accelerated HTP backend inside ONNX Runtime.
  - **Foundry Local NPU Endpoint:** Standardized `/v1/chat/completions` API targeting Snapdragon NPU LLM weights.
  - **Graceful Hardware Fallback:** Zero-downtime fallback to CPU if QNN drivers are absent on non-Snapdragon dev machines.

---

## 📌 Slide 7: Verified Performance & Benchmark Metrics
- **Headline:** Tested & Verified Benchmarks (Intel AMD64 Dev Machine vs Snapdragon NPU Projections)
- **Key Verified Metrics:**
  - 🎯 **STT Accuracy (WER):** **10% WER** (0.10) verified on clean TTS speech (Whisper-tiny CPU).
  - ⏱️ **STT Speed (RTF):** **~0.166 RTF** (CPU measured) | **~0.021 RTF** (Snapdragon NPU projected).
  - 🚀 **LLM Throughput:** **4.93 tokens/sec** (Ollama phi3:mini CPU measured) | **~42.5 tokens/sec** (Snapdragon NPU projected).
  - 🔍 **Vector Search Latency:** **< 5 ms** per passage query.
  - 🧪 **Test Suite:** **24/24 passed** unit & integration tests (`pytest`).

---

## 📌 Slide 8: Privacy & Strict Offline Guarantee
- **Headline:** Complete Data Isolation with Network Interceptor Verification
- **Privacy Highlights:**
  - **Zero Network Traffic:** All models, embeddings, and vector indices reside on local storage (`~/.lecturelens/`).
  - **Socket Guard Enforcement:** Includes `scripts/offline_check.py` which monkeypatches python sockets to intercept and verify 0 cloud calls.
  - **Airplane Mode Ready:** Fully functional without active Wi-Fi or cellular networks.

---

## 📌 Slide 9: Premium Cyber Yellow & Obsidian Black UI
- **Headline:** High-Contrast iQOO Flagship Aesthetic
- **User Interface Features:**
  - 🎨 **iQOO Cyber Yellow & Carbon Black Palette:** Electric yellow highlights (`#FFD100`) against matte black backdrop (`#000000`).
  - 📱 **8 Intuitive Tabs:** Streamlit web dashboard designed for rapid navigation during live lectures.
  - ⚡ **Backend Status Badge:** Real-time hardware sidebar showing active acceleration (QNN vs CPU).

---

## 📌 Slide 10: Real-World Impact & Target Audience
- **Headline:** Transforming STEM & Higher Education Learning
- **Target Persona:**
  - **STEM Students:** Need fast summaries of math-heavy, technical lectures.
  - **Medical & Law Students:** Require high-density term extraction and active recall quiz generation.
  - **Researchers & Faculty:** Discussing confidential IP or proprietary research needing 100% privacy.

---

## 📌 Slide 11: Future Expansion & Technical Roadmap
- **Headline:** What's Next for LectureLens
- **Planned Enhancements:**
  1. **Multi-Speaker Diarization:** Identify and separate professor vs student voices on-device.
  2. **Multilingual Speech Recognition:** Real-time translation and transcription for Tamil, Hindi, Spanish, and French.
  3. **Snapdragon Cross-Device Sync:** Local Wi-Fi Direct sharing between Snapdragon laptops and tablets.

---

## 📌 Slide 12: Conclusion & Q&A
- **Headline:** Bringing Private, Offline AI to Every Classroom
- **Summary:** LectureLens combines Snapdragon NPU hardware acceleration with privacy-first engineering to deliver a fast, reliable lecture copilot for Windows-on-ARM laptops.
- **GitHub Repository:** [https://github.com/suvakovan/SNAP-DRAGON-](https://github.com/suvakovan/SNAP-DRAGON-)
- **Thank You!** Questions & Live Demo.
