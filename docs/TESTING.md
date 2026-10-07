# Testing Guide

## Running Tests

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_audio.py -v

# Run only unit tests
pytest tests/ -v -m unit

# Run with coverage
pytest tests/ --cov=lecturelens --cov-report=term-missing
```

## Test Categories

| Test File | Coverage Area |
|---|---|
| `test_audio.py` | Audio preprocessing and VAD detection |
| `test_chunker.py` | Audio windowing and overlap |
| `test_notes_schema.py` | Pydantic schema validation, JSON repair |
| `test_search.py` | Hybrid search indexing and retrieval |
| `test_backend_detect.py` | Hardware detection report structure |
| `test_qa.py` | Citation parsing and Q&A context formatting |
| `test_wer.py` | Word Error Rate calculation |
| `test_no_simulation_in_prod.py` | Backend factory integrity guard |
| `test_preprocess_edge_cases.py` | Edge cases in audio loading |
| `test_vad_edge_cases.py` | VAD boundary conditions |
| `test_chunker_edge_cases.py` | Chunker boundary conditions |
| `test_json_repair.py` | LLM JSON output repair |
| `test_session_model.py` | Session serialization roundtrip |
| `test_exports.py` | Export format validation |
| `test_config.py` | Configuration defaults |
| `test_transcribe_dedup.py` | Overlap deduplication |

## Writing New Tests

1. Create test file in `tests/` with `test_` prefix
2. Use shared fixtures from `tests/conftest.py`
3. Mark unit tests with `@pytest.mark.unit`
4. Follow AAA pattern: Arrange, Act, Assert
