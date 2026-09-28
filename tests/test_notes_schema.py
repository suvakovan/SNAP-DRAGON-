"""
Tests for notes schema validation and JSON repair utilities.
"""

import pytest
from lecturelens.backends.llm_cpu import CPULLMBackend
from lecturelens.pipeline.notes import clean_and_parse_json, generate_full_notes, QuizQuestion


def test_clean_and_parse_json_valid():
    raw_text = '```json\n{"summary": ["Point 1"], "key_terms": [], "revision_paragraph": "Revise."}\n```'
    parsed = clean_and_parse_json(raw_text)
    assert parsed["summary"] == ["Point 1"]


def test_clean_and_parse_json_repair_trailing_comma():
    raw_text = '{"summary": ["Point 1",], "key_terms": [], "revision_paragraph": "Revise.",}'
    parsed = clean_and_parse_json(raw_text)
    assert parsed["summary"] == ["Point 1"]


def test_quiz_question_validation():
    valid_q = {
        "question": "What is NPU?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "explanation": "A is correct."
    }
    q = QuizQuestion(**valid_q)
    assert q.correct_index == 0

    # Test duplicate options validation
    invalid_q = {
        "question": "What is NPU?",
        "options": ["A", "A", "C", "D"],
        "correct_index": 0,
        "explanation": "A is correct."
    }
    with pytest.raises(ValueError):
        QuizQuestion(**invalid_q)

    # Test index out of range validation
    invalid_idx = {
        "question": "What is NPU?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 5,
        "explanation": "Out of range."
    }
    with pytest.raises(ValueError):
        QuizQuestion(**invalid_idx)


def test_generate_full_notes_end_to_end():
    transcript = "This lecture discusses hardware acceleration and Neural Processing Units."
    notes = generate_full_notes(transcript, backend_preference="cpu")
    assert len(notes.summary) > 0
    assert len(notes.key_terms) > 0
    assert len(notes.quiz) > 0
    assert len(notes.flashcards) > 0
    assert "device" in notes.llm_metrics
