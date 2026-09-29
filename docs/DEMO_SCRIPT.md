# LectureLens Demo Script (CPU-Verified Build)

> **Note for presenter:** This machine runs on Intel AMD64 (no Snapdragon NPU). The sidebar shows `CPU Fallback` for STT and LLM — this is honest and expected. The NPU code paths exist in the repo but require Snapdragon X hardware to activate.

## Video Timestamp Breakdown (~90 seconds)

- **0:00 - 0:10 | The Problem**
  - "Engineering students face long lectures and poor campus Wi-Fi. Uploading private audio to cloud services adds latency and privacy risks."

- **0:10 - 0:25 | App Launch & Offline Guarantee**
  - Open `http://localhost:8501`. Point to the sidebar: "The app shows our hardware backend — CPU Fallback on this development machine, with a QNN/NPU code path ready for Snapdragon X hardware."
  - "The ONLINE MODE badge confirms no cloud requests are made — zero external API calls."

- **0:25 - 0:55 | Record/Upload & Transcription**
  - Click **📁 History** tab → click **📖 Open** on the pre-processed session to load instantly.
  - Switch to **📝 Notes & Summary** tab. Show the executive summary bullets, key terms, and revision paragraph.
  - Point to the metrics strip: "STT ran on CPU. No cloud, no latency."

- **0:55 - 1:15 | Interactive Quiz**
  - Click **❓ Interactive Quiz** tab. Show the quiz questions.
  - Select an answer for Q1 and click **Check Answer Q1**. Show the ✅ correct / ❌ incorrect feedback and explanation.

- **1:15 - 1:30 | Flashcards**
  - Click **🎴 Flashcards** tab. Click to expand a flashcard and show the answer.

- **1:30 - 1:45 | Performance Tab**
  - Click **📊 Performance** tab. Show the benchmark note (or the metrics from backend info visible on the Notes tab).

- **1:45 - 1:50 | Closing**
  - "LectureLens brings private, offline AI-powered lecture assistance — fully functional on CPU today, with NPU acceleration code-ready for Snapdragon X hardware."
