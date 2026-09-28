"""
Quiz pipeline module.
"""

from typing import List
from lecturelens.backends import get_llm_backend
from lecturelens.pipeline.notes import generate_quiz, QuizQuestion


def generate_lecture_quiz(
    transcript: str, backend_preference: str = "auto", num_questions: int = 5
) -> List[QuizQuestion]:
    """Thin wrapper to generate quiz questions from transcript."""
    backend = get_llm_backend(backend_preference)
    quiz_data, _ = generate_quiz(transcript, backend, num_questions=num_questions)
    return quiz_data.questions
