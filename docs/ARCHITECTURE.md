# LectureLens Architecture Documentation

## Overview

LectureLens is an offline lecture copilot engineered specifically for Snapdragon X Windows-on-ARM laptops. The architecture prioritizes privacy, low latency, and hardware acceleration on Qualcomm Hexagon NPUs with strict CPU fallback guarantees.

## System Architecture Diagram

```mermaid
graph TD
    A[Microphone / Audio File] --> B[Audio Preprocessor & Mono Resampler]
    B --> C[Energy VAD & Audio Chunker]
    C --> D{STT Engine Selector}
    D -->|NPU Available| E[Whisper STT - Qualcomm QNN / HTP]
    D -->|CPU Fallback| F[Whisper STT - ONNX Runtime CPU]
    E --> G[Full Transcript & Segment Timestamps]
    F --> G
    G --> H{LLM Engine Selector}
    H -->|NPU Available| I[Foundry Local - NPU Instruct Variant]
    H -->|CPU Fallback| J[Local CPU LLM Engine]
    I --> K[Summary, Key Terms & Revision Paragraph]
    I --> L[Validated Multiple Choice Quiz]
    I --> M[Active Recall Flashcards]
    J --> K
    J --> L
    J --> M
    G --> N[MiniLM Embedding Generator]
    N --> O[Hybrid Vector & Keyword Search Index]
    K --> P[Session JSON & Markdown Exporter]
    L --> P
    M --> P
    P --> Q[Streamlit Web UI Dashboard]
    O --> Q
```

## Key Architectural Principles

1. **Hardware Acceleration First:** Leverages `QNNExecutionProvider` (HTP backend) for speech recognition and Microsoft Foundry Local for NPU-accelerated LLM inferencing.
2. **Zero Cloud Dependency:** Operates 100% offline with socket guard validation (`scripts/offline_check.py`).
3. **Resilient Abstraction:** All AI runtimes sit behind abstract interfaces (`STTBackend`, `LLMBackend`, `EmbedBackend`).
4. **Energy VAD Filtering:** Uses RMS frame energy detection to skip silent intervals and conserve battery.
