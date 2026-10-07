# LectureLens API Reference

## Core Pipeline

### `run_full_pipeline(audio_source, title, progress_callback, stt_preference, llm_preference)`
Orchestrates end-to-end processing: audio â†’ transcription â†’ notes â†’ session storage.

**Parameters:**
- `audio_source` â€” File path (str/Path) or numpy array (float32, 16kHz mono)
- `title` â€” Session title string
- `progress_callback` â€” Optional `Callable[[str, float], None]` for UI progress
- `stt_preference` â€” `"auto"`, `"npu"`, or `"cpu"`
- `llm_preference` â€” `"auto"`, `"npu"`, or `"cpu"`

**Returns:** `LectureSession` Pydantic model

---

## Audio Module (`lecturelens.audio`)

### `load_audio(file_path, target_sample_rate=16000)`
Loads WAV/MP3/FLAC, converts to mono float32, resamples, normalizes.

### `preprocess_audio(data, original_sample_rate, target_sample_rate)`
Processes raw numpy audio: stereoâ†’mono, resample, peak normalize.

### `chunk_audio(audio, sample_rate, chunk_seconds, overlap_seconds)`
Splits long audio into overlapping windows with energy-based boundary cuts.

### `is_speech(audio, threshold, sample_rate)`
Quick VAD check â€” returns `True` if RMS energy exceeds threshold.

### `detect_speech_spans(audio, sample_rate, threshold, frame_ms, min_silence_ms)`
Returns list of `(start_sec, end_sec)` tuples for detected speech regions.

---

## Backend Factories (`lecturelens.backends`)

### `get_stt_backend(preference="auto")` â†’ `STTBackend`
### `get_llm_backend(preference="auto")` â†’ `LLMBackend`
### `get_embed_backend(preference="auto")` â†’ `EmbedBackend`

Each raises `BackendUnavailable` if no real backend can be loaded.

---

## Notes Pipeline (`lecturelens.pipeline.notes`)

### `generate_full_notes(transcript, backend_preference, num_quiz, num_cards)`
Returns `LectureNotes` with summary, key terms, quiz, flashcards, and metrics.

### `clean_and_parse_json(text)`
Repairs and parses LLM JSON output (strips markdown blocks, fixes trailing commas).

---

## Search (`lecturelens.pipeline.search`)

### `SearchIndex.build_index(sessions=None)`
Indexes all sessions into vector embeddings + passage metadata.

### `SearchIndex.search(query, top_k=5, hybrid_weight=0.7)`
Hybrid vector+keyword search. Returns `List[Tuple[float, Dict]]`.

---

## Storage (`lecturelens.storage`)

### `save_session(session)` / `load_session(session_id)` / `list_sessions()` / `delete_session(session_id)`
JSON-based session persistence in `data/sessions/`.

### Export Functions
- `export_markdown(session)` â€” Formatted Markdown notes
- `export_anki_csv(session)` â€” Anki-compatible flashcard CSV
- `export_srt(session)` â€” SRT subtitle file
- `export_plain_transcript(session)` â€” Timestamped plain text
- `export_study_sheet(session)` â€” Complete Markdown study sheet
