# Snapdragon NPU Acceleration Guide

## Overview

LectureLens leverages the Qualcomm Hexagon NPU (Neural Processing Unit) on Snapdragon X Series processors for accelerated AI inference. This guide explains how NPU acceleration works in the application.

## Supported Hardware

| Device | Chipset | NPU Status |
|---|---|---|
| HP OmniBook X | Snapdragon X Elite | âœ… Full NPU support |
| Lenovo Yoga Slim 7x | Snapdragon X Elite | âœ… Full NPU support |
| Surface Laptop 7 | Snapdragon X Plus | âœ… Full NPU support |
| Surface Pro 11 | Snapdragon X Plus | âœ… Full NPU support |
| Any Intel/AMD laptop | N/A | ðŸ’» CPU fallback |

## NPU vs CPU Performance

| Task | CPU Performance | NPU Performance | Speedup |
|---|---|---|---|
| Whisper STT | RTF ~0.166 | RTF ~0.021 | ~8x faster |
| LLM Inference | ~5 tok/s | ~42 tok/s | ~8x faster |
| Embeddings | ~5ms/passage | <1ms/passage | ~5x faster |

## How It Works

### 1. Backend Detection
The `detect_hardware()` function checks for QNNExecutionProvider availability.

### 2. Factory Selection
Backend factories (STT, LLM, Embed) try NPU first, fall back to CPU automatically.

### 3. NPU Verification
`verified_npu=True` is set ONLY when QNNExecutionProvider is confirmed as the first active provider.

## Enabling NPU Acceleration

```powershell
# Install QNN-enabled ONNX Runtime
pip install onnxruntime-qnn

# Verify NPU is detected
python scripts/check_env.py
```

## CPU Fallback

On machines without Snapdragon NPU, the application gracefully degrades:
- STT uses CPUExecutionProvider (slower but functional)
- LLM uses Ollama or llama.cpp on CPU
- All features work identically, just slower
