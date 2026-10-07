# Deployment Guide

## Local Development

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run.ps1
```

## Production Deployment (Snapdragon X Target)

### Hardware Verification
```powershell
python scripts/check_env.py
python scripts/env_proof.py
```

### NPU Acceleration Checklist

- [ ] Snapdragon X Elite/Plus device with Windows 11 ARM64
- [ ] Qualcomm QNN SDK installed
- [ ] `onnxruntime-qnn` package installed
- [ ] Whisper ONNX models downloaded to `models/whisper-base-en/`
- [ ] MiniLM ONNX model downloaded to `models/all-MiniLM-L6-v2/`
- [ ] Microsoft Foundry Local installed (optional, for NPU LLM)

### Performance Validation
```powershell
python scripts/benchmark.py --quick
python scripts/consistency_check.py
python scripts/quality_check.py
```

### Offline Verification
```powershell
python scripts/offline_check.py
```

## Environment Variables

See `.env.example` for all configurable options. Copy to `.env` and modify as needed:

```powershell
cp .env.example .env
```
