# LectureLens Setup Guide

Complete setup instructions for Windows 11 ARM64 (Snapdragon X Series).

## Prerequisites

| Requirement | Minimum | Recommended |
|---|---|---|
| OS | Windows 11 ARM64 | Windows 11 24H2 |
| Python | 3.11 | 3.12 (ARM64 native) |
| RAM | 8 GB | 16 GB |
| Storage | 2 GB free | 5 GB free |
| Device | Any Windows PC | Snapdragon X Elite/Plus |

## Step 1: Install Python (ARM64 Native)

Download Python 3.12 ARM64 from [python.org](https://www.python.org/downloads/). Ensure "Add to PATH" is checked during installation.

```powershell
python --version  # Should show 3.12.x
```

## Step 2: Clone Repository

```powershell
git clone https://github.com/suvakovan/SNAP-DRAGON-.git
cd SNAP-DRAGON-
```

## Step 3: Automated Setup

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```

This script:
1. Creates a Python virtual environment (`.venv`)
2. Installs all dependencies from `requirements.txt`
3. Creates required directories (`data/`, `models/`, `logs/`)
4. Downloads model assets (Whisper ONNX, MiniLM embeddings)

## Step 4: Start a Local LLM (Required for Notes/Quiz)

### Option A: Ollama (Recommended)
```powershell
# Install Ollama from https://ollama.ai
ollama serve
ollama pull phi3:mini
```

### Option B: llama.cpp Server
```powershell
llama-server -m path/to/model.gguf --port 8080
```

## Step 5: Launch LectureLens

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run.ps1
```

The Streamlit UI opens at `http://localhost:8501`.

## Step 6: Verify Offline Capability

```powershell
python scripts/offline_check.py
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Activate venv: `.\.venv\Scripts\Activate` |
| No microphone detected | Check Windows audio device settings |
| Ollama connection refused | Run `ollama serve` in separate terminal |
| QNN provider not found | Install `onnxruntime-qnn` package |
