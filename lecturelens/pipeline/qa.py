"""
Grounded Q&A pipeline — answers student questions from retrieved lecture passages only.
"""

import re
import time
from typing import List, Tuple, Dict, Any, Optional

from lecturelens.pipeline.search import SearchIndex
from lecturelens.backends.base import LLMBackend, BackendUnavailable
from lecturelens.logging_setup import logger


_QA_SYSTEM = """You are a helpful academic assistant. Answer the student's question using ONLY the passage excerpts provided below.
Rules:
- Cite passage numbers like [1], [2] when using information from those passages.
- If the answer cannot be found in the provided passages, respond exactly with: "The lecture does not cover this."
- Do not use any information not present in the provided passages.
- Keep your answer concise (2-4 sentences).
"""


def build_qa_context(passages: List[Tuple[float, Dict[str, Any]]]) -> str:
    """Formats retrieved passages into a numbered context string."""
    lines = []
    for i, (score, passage) in enumerate(passages, 1):
        ts = passage.get("timestamp_sec", 0)
        text = passage.get("text", "")
        lines.append(f"[{i}] (at {ts}s): {text}")
    return "\n".join(lines)


def parse_citations(answer_text: str, num_passages: int) -> List[int]:
    """Extracts valid citation references [n] from answer text."""
    matches = re.findall(r"\[(\d+)\]", answer_text)
    valid = []
    for m in matches:
        idx = int(m)
        if 1 <= idx <= num_passages and idx not in valid:
            valid.append(idx)
    return valid


def ask_lecture(
    query: str,
    search_index: SearchIndex,
    llm_backend: LLMBackend,
    top_k: int = 4
) -> Dict[str, Any]:
    """
    End-to-end grounded Q&A:
    1. Retrieve top_k passages from hybrid search.
    2. Generate grounded answer with citation rules.
    3. Map citations back to passage timestamps.
    """
    t_retrieval_start = time.time()
    results = search_index.search(query, top_k=top_k)
    retrieval_time = round(time.time() - t_retrieval_start, 3)

    if not results:
        return {
            "answer": "No lecture content has been indexed yet. Process a lecture first.",
            "citations": [],
            "retrieval_time_sec": retrieval_time,
            "generation_time_sec": 0.0,
            "top_k": top_k
        }

    context = build_qa_context(results)
    user_prompt = f"Context passages:\n{context}\n\nStudent Question: {query}"

    t_gen_start = time.time()
    llm_result = llm_backend.generate(
        system=_QA_SYSTEM,
        user=user_prompt,
        max_tokens=300,
        temperature=0.1
    )
    generation_time = round(time.time() - t_gen_start, 3)

    answer = llm_result.text.strip()
    citation_indices = parse_citations(answer, len(results))

    cited_passages = []
    for idx in citation_indices:
        _, passage = results[idx - 1]
        cited_passages.append({
            "citation_num": idx,
            "timestamp_sec": passage.get("timestamp_sec", 0),
            "session_title": passage.get("session_title", ""),
            "excerpt": passage.get("text", "")[:200]
        })

    return {
        "answer": answer,
        "citations": cited_passages,
        "retrieval_time_sec": retrieval_time,
        "generation_time_sec": generation_time,
        "top_k": top_k
    }
