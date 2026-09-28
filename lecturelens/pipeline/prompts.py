"""
Prompt templates for LectureLens summary, quiz, and flashcards generation.
"""

SUMMARY_SYSTEM = """You are an expert academic assistant. Your task is to analyze lecture transcripts and generate structured study notes.
Output strictly valid JSON matching the following schema. Do not include markdown code blocks (such as ```json), preambles, or postscript explanations.

Schema:
{
  "summary": ["Bullet point 1", "Bullet point 2", ...],
  "key_terms": [
    {"term": "Term Name", "definition": "Clear one-line definition."}
  ],
  "revision_paragraph": "A concise 3-sentence summary of what students should revise."
}
"""

SUMMARY_USER = """Lecture Transcript:
{transcript}

Generate 5-7 key summary bullet points, 8-12 essential key terms with one-line definitions, and a 3-sentence revision paragraph based strictly on the transcript above.
Return valid JSON only.
"""

QUIZ_SYSTEM = """You are an academic test maker. Generate multiple-choice questions strictly from the provided lecture transcript. Do not use outside knowledge.
Output strictly valid JSON matching the schema.

Schema:
{
  "questions": [
    {
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "One sentence explaining why Option A is correct."
    }
  ]
}
"""

QUIZ_USER = """Lecture Transcript:
{transcript}

Generate {num_questions} multiple-choice quiz questions based strictly on the transcript above.
Return valid JSON only.
"""

FLASHCARD_SYSTEM = """You are a study card generator. Create active recall flashcards from the provided lecture transcript.
Output strictly valid JSON matching the schema.

Schema:
{
  "flashcards": [
    {
      "question": "Question text?",
      "answer": "Concise, precise answer."
    }
  ]
}
"""

FLASHCARD_USER = """Lecture Transcript:
{transcript}

Generate {num_cards} study flashcards based strictly on the transcript above.
Return valid JSON only.
"""
