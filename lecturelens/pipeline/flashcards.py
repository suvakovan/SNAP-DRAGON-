"""
Flashcards pipeline module.
"""

from typing import List
from lecturelens.backends import get_llm_backend
from lecturelens.pipeline.notes import generate_flashcards, Flashcard


def generate_lecture_flashcards(
    transcript: str, backend_preference: str = "auto", num_cards: int = 5
) -> List[Flashcard]:
    """Thin wrapper to generate flashcards from transcript."""
    backend = get_llm_backend(backend_preference)
    flash_data, _ = generate_flashcards(transcript, backend, num_cards=num_cards)
    return flash_data.flashcards
