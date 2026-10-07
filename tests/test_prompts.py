"""Tests for prompt templates."""

from lecturelens.pipeline.prompts import (
    SUMMARY_SYSTEM, SUMMARY_USER, QUIZ_SYSTEM, QUIZ_USER,
    FLASHCARD_SYSTEM, FLASHCARD_USER,
)


class TestPromptTemplates:
    def test_summary_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in SUMMARY_SYSTEM

    def test_summary_user_has_placeholder(self):
        assert "{transcript}" in SUMMARY_USER

    def test_quiz_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in QUIZ_SYSTEM

    def test_quiz_user_has_placeholders(self):
        assert "{transcript}" in QUIZ_USER
        assert "{num_questions}" in QUIZ_USER

    def test_flashcard_system_has_grounding_rule(self):
        assert "GROUNDING RULE" in FLASHCARD_SYSTEM

    def test_flashcard_user_has_placeholders(self):
        assert "{transcript}" in FLASHCARD_USER
        assert "{num_cards}" in FLASHCARD_USER

    def test_summary_user_format(self):
        result = SUMMARY_USER.format(transcript="Hello world")
        assert "Hello world" in result

    def test_quiz_user_format(self):
        result = QUIZ_USER.format(transcript="Test", num_questions=5)
        assert "Test" in result
        assert "5" in result
