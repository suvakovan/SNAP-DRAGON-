"""
Lecture notes generator: summary, key terms, revision paragraph, quiz, and flashcards.
Robust JSON repair and schema validation via Pydantic.
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, field_validator

from lecturelens.backends import get_llm_backend
from lecturelens.backends.base import LLMBackend, LLMResult
from lecturelens.pipeline.prompts import (
    SUMMARY_SYSTEM, SUMMARY_USER,
    QUIZ_SYSTEM, QUIZ_USER,
    FLASHCARD_SYSTEM, FLASHCARD_USER
)
from lecturelens.config import config
from lecturelens.logging_setup import logger


# --- Pydantic Data Schemas ---

class KeyTerm(BaseModel):
    term: str
    definition: str


class SummaryData(BaseModel):
    summary: List[str]
    key_terms: List[KeyTerm]
    revision_paragraph: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str

    @field_validator("options")

    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("Quiz question must have exactly 4 options.")
        if len(set(v)) != len(v):
            raise ValueError("Quiz options must be unique.")
        return v

    @field_validator("correct_index")

    def validate_index(cls, v):
        if not (0 <= v <= 3):
            raise ValueError("correct_index must be between 0 and 3.")
        return v


class QuizData(BaseModel):
    questions: List[QuizQuestion]


class Flashcard(BaseModel):
    question: str
    answer: str


class FlashcardData(BaseModel):
    flashcards: List[Flashcard]


class LectureNotes(BaseModel):
    summary: List[str]
    key_terms: List[KeyTerm]
    revision_paragraph: str
    quiz: List[QuizQuestion]
    flashcards: List[Flashcard]
    llm_metrics: Dict[str, Any]


# --- JSON Parsing & Repair Utility ---

def clean_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Cleans, repairs, and parses JSON output from LLM.
    Strips markdown code blocks, fixes trailing commas, smart quotes, etc.
    """
    cleaned = text.strip()

    # Remove markdown block backticks if present
    if "```" in cleaned:
        cleaned = re.sub(r"```[a-zA-Z]*\n?", "", cleaned)
        cleaned = cleaned.replace("```", "").strip()

    # Try standard parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Extract first JSON object or array
    json_match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)

    # Replace smart quotes with standard quotes
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("’", "'")

    # Fix trailing commas before } or ]
    cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to repair JSON output: {e}\nRaw Text:\n{text}")
        raise ValueError(f"Could not parse valid JSON from LLM output: {e}")


# --- Generator Functions ---

def generate_summary(
    transcript: str, backend: LLMBackend
) -> Tuple[SummaryData, LLMResult]:
    """Generates summary bullets, key terms, and revision paragraph."""
    # Handle map-reduce for long transcripts (> 1500 words)
    words = transcript.split()
    if len(words) > 1500:
        chunk_size = 1200
        sub_transcripts = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        intermediate_summaries = []
        for sub in sub_transcripts:
            res = backend.generate(SUMMARY_SYSTEM, SUMMARY_USER.format(transcript=sub), json_mode=True)
            data = clean_and_parse_json(res.text)
            intermediate_summaries.extend(data.get("summary", []))
        transcript = "Summary of parts: " + " ".join(intermediate_summaries)

    user_prompt = SUMMARY_USER.format(transcript=transcript)
    res = backend.generate(SUMMARY_SYSTEM, user_prompt, json_mode=True)
    try:
        data = clean_and_parse_json(res.text)
        parsed = SummaryData(**data)
        return parsed, res
    except Exception:
        # Retry once with explicit json hint
        logger.warning("Retrying LLM summary generation with strict JSON prompt.")
        res_retry = backend.generate("Return valid JSON only matching the schema.", user_prompt, json_mode=True)
        data = clean_and_parse_json(res_retry.text)
        parsed = SummaryData(**data)
        return parsed, res_retry


def generate_quiz(
    transcript: str, backend: LLMBackend, num_questions: int = 5
) -> Tuple[QuizData, LLMResult]:
    """Generates quiz questions with schema validation."""
    user_prompt = QUIZ_USER.format(transcript=transcript, num_questions=num_questions)
    res = backend.generate(QUIZ_SYSTEM, user_prompt, json_mode=True)
    try:
        data = clean_and_parse_json(res.text)
        parsed = QuizData(**data)
        return parsed, res
    except Exception as e:
        logger.warning(f"Retrying quiz generation due to schema error: {e}")
        res_retry = backend.generate("Return strictly valid JSON only.", user_prompt, json_mode=True)
        data = clean_and_parse_json(res_retry.text)
        parsed = QuizData(**data)
        return parsed, res_retry


def generate_flashcards(
    transcript: str, backend: LLMBackend, num_cards: int = 5
) -> Tuple[FlashcardData, LLMResult]:
    """Generates flashcards with schema validation."""
    user_prompt = FLASHCARD_USER.format(transcript=transcript, num_cards=num_cards)
    res = backend.generate(FLASHCARD_SYSTEM, user_prompt, json_mode=True)
    try:
        data = clean_and_parse_json(res.text)
        parsed = FlashcardData(**data)
        return parsed, res
    except Exception as e:
        logger.warning(f"Retrying flashcard generation due to schema error: {e}")
        res_retry = backend.generate("Return strictly valid JSON only.", user_prompt, json_mode=True)
        data = clean_and_parse_json(res_retry.text)
        parsed = FlashcardData(**data)
        return parsed, res_retry


def generate_full_notes(
    transcript: str, backend_preference: str = "auto", num_quiz: int = 5, num_cards: int = 5
) -> LectureNotes:
    """Generates complete lecture notes package including metrics."""
    backend = get_llm_backend(backend_preference)
    start_all = time.time()

    summary_data, summary_res = generate_summary(transcript, backend)
    quiz_data, quiz_res = generate_quiz(transcript, backend, num_questions=num_quiz)
    flash_data, flash_res = generate_flashcards(transcript, backend, num_cards=num_cards)

    total_time = time.time() - start_all

    metrics = {
        "device": backend.info.device,
        "runtime": backend.info.runtime,
        "verified_npu": backend.info.verified_npu,
        "total_seconds": round(total_time, 2),
        "tokens_per_second": round(summary_res.tokens_per_second or 0.0, 2),
        "time_to_first_token": summary_res.time_to_first_token
    }

    return LectureNotes(
        summary=summary_data.summary,
        key_terms=summary_data.key_terms,
        revision_paragraph=summary_data.revision_paragraph,
        quiz=quiz_data.questions,
        flashcards=flash_data.flashcards,
        llm_metrics=metrics
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate lecture notes from text transcript.")
    parser.add_argument("--transcript", type=str, required=True, help="Path to transcript text file")
    parser.add_argument("--backend", type=str, default="auto", choices=["auto", "npu", "cpu"])
    args = parser.parse_args()

    with open(args.transcript, "r", encoding="utf-8") as f:
        text_content = f.read()

    notes = generate_full_notes(text_content, backend_preference=args.backend)
    print("\n=== LECTURE NOTES ===")
    print(json.dumps(notes.model_dump(), indent=2))
