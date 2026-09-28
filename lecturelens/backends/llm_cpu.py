"""
CPU LLM Backend (fallback / local CPU generation).
"""

import time
from typing import Optional
from lecturelens.backends.base import LLMBackend, BackendInfo, LLMResult
from lecturelens.logging_setup import logger


class CPULLMBackend(LLMBackend):
    def __init__(self, model_name: str = "cpu-fallback-llm"):
        self.model_name = model_name
        self.info = BackendInfo(
            name=model_name,
            runtime="cpu-fallback",
            device="CPU",
            verified_npu=False,
            details={"type": "python-mock-fallback"}
        )

    def load(self) -> None:
        """Load CPU LLM backend."""
        logger.info("Loaded CPU LLM Backend.")

    def generate(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResult:
        """Generate CPU response."""
        start_t = time.time()
        
        # Skeleton JSON output for tests & offline operation when no local LLM server running
        if "quiz" in system.lower() or "quiz" in user.lower():
            text = '{"questions": [{"question": "What is the primary topic of the lecture?", "options": ["Architecture", "Physics", "Chemistry", "Biology"], "correct_index": 0, "explanation": "The lecture discusses architecture."}]}'
        elif "flashcard" in system.lower() or "flashcard" in user.lower():
            text = '{"flashcards": [{"question": "What is NPU?", "answer": "Neural Processing Unit."}]}'
        else:
            text = '{"summary": ["Key point 1 of the lecture.", "Key point 2 of the lecture."], "key_terms": [{"term": "NPU", "definition": "Neural Processing Unit for hardware acceleration."}], "revision_paragraph": "Students should review key concepts in system architecture."}'

        total_seconds = max(time.time() - start_t, 0.01)
        token_count = len(text.split())
        tps = token_count / total_seconds

        return LLMResult(
            text=text,
            prompt_tokens=len(user.split()),
            completion_tokens=token_count,
            time_to_first_token=0.01,
            total_seconds=total_seconds,
            tokens_per_second=tps
        )
