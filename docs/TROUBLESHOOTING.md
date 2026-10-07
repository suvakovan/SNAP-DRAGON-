# Troubleshooting Guide

## Common Issues

### 1. Backend Unavailable Errors

**Symptom:** `BackendUnavailable: Whisper ONNX model files not found`

**Solution:**
```powershell
python scripts/download_models.py
```

### 2. No Microphone Input

**Symptom:** `RuntimeError: No microphone input devices available`

**Solution:**
- Check Windows Sound Settings â†’ Input devices
- Ensure microphone permissions are granted
- Try `python -c "import sounddevice; print(sounddevice.query_devices())"`

### 3. LLM Connection Refused

**Symptom:** `BackendUnavailable: No real local LLM found`

**Solution:**
```powershell
# Start Ollama server
ollama serve
# Pull a model
ollama pull phi3:mini
```

### 4. QNN Provider Not Available

**Symptom:** `QNNExecutionProvider not available`

**Explanation:** This is expected on non-Snapdragon hardware. The app automatically falls back to CPU.

**For Snapdragon devices:**
```powershell
pip install onnxruntime-qnn
```

### 5. Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'lecturelens'`

**Solution:**
```powershell
.\.venv\Scripts\Activate
pip install -e .
```

### 6. Streamlit Port Conflict

**Symptom:** `Address already in use`

**Solution:**
```powershell
streamlit run lecturelens/ui/app.py --server.port 8502
```

### 7. JSON Parse Errors from LLM

**Symptom:** `ValueError: Could not parse valid JSON from LLM output`

**Explanation:** The LLM occasionally returns malformed JSON. The `clean_and_parse_json` utility auto-repairs common issues (trailing commas, smart quotes, markdown wrappers). If errors persist, try a different model or increase `llm_max_tokens`.
