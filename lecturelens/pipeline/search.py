"""
Semantic and hybrid search pipeline for lecture transcripts using vector embeddings and BM25 keyword scoring.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from lecturelens.backends import get_embed_backend
from lecturelens.backends.base import BackendUnavailable
from lecturelens.backends.embed_onnx import DeterministicEmbedBackend
from lecturelens.pipeline.session import LectureSession
from lecturelens.storage.store import list_sessions
from lecturelens.config import config
from lecturelens.logging_setup import logger


def chunk_transcript_into_passages(
    session: LectureSession, passage_word_count: int = 60
) -> List[Dict[str, Any]]:
    """Splits transcript into passage blocks of ~60 words with session metadata."""
    words = session.transcript.split()
    if not words:
        return []

    passages = []
    for i in range(0, len(words), passage_word_count):
        passage_text = " ".join(words[i:i + passage_word_count])
        # Approximate timestamp based on word position
        fraction = i / float(len(words))
        approx_timestamp = fraction * session.metadata.audio_duration_seconds

        passages.append({
            "session_id": session.metadata.id,
            "session_title": session.metadata.title,
            "timestamp_sec": round(approx_timestamp, 1),
            "text": passage_text
        })
    return passages


class SearchIndex:
    """In-memory and file-backed hybrid search index."""

    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or (config.data_dir / "search_index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.passages: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        try:
            self.embed_backend = get_embed_backend()
        except BackendUnavailable as e:
            logger.warning(f"SearchIndex: Real embedding backend unavailable ({e}). Using deterministic fallback for search.")
            self.embed_backend = DeterministicEmbedBackend()

    def build_index(self, sessions: Optional[List[LectureSession]] = None) -> None:
        """Indexes all sessions into vectors and passage metadata."""
        if sessions is None:
            sessions = list_sessions()

        all_passages: List[Dict[str, Any]] = []
        for s in sessions:
            all_passages.extend(chunk_transcript_into_passages(s))

        self.passages = all_passages
        if not all_passages:
            self.embeddings = np.empty((0, 384), dtype=np.float32)
            return

        texts = [p["text"] for p in all_passages]
        self.embeddings = self.embed_backend.embed(texts)

        # Save to disk
        np.save(str(self.index_dir / "vectors.npy"), self.embeddings)
        with open(self.index_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(all_passages, f, indent=2)

        logger.info(f"Built search index with {len(all_passages)} passages.")

    def search(
        self, query: str, top_k: int = 5, hybrid_weight: float = 0.7
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Performs hybrid (vector + keyword) similarity search across indexed passages.
        Returns list of (score, passage_metadata).
        """
        if not self.passages or self.embeddings is None or len(self.embeddings) == 0:
            self.build_index()

        if not self.passages or self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Vector Cosine Similarity
        query_vec = self.embed_backend.embed([query])[0]
        # Vectors are L2 normalized, dot product equals cosine similarity
        vector_scores = np.dot(self.embeddings, query_vec)

        # Keyword TF-IDF / BM25 Score Approximation
        query_terms = query.lower().split()
        keyword_scores = []
        for p in self.passages:
            text_lower = p["text"].lower()
            match_count = sum(1 for term in query_terms if term in text_lower)
            score = match_count / float(max(len(query_terms), 1))
            keyword_scores.append(score)

        keyword_scores = np.array(keyword_scores, dtype=np.float32)

        # Hybrid Combination
        combined_scores = (hybrid_weight * vector_scores) + ((1.0 - hybrid_weight) * keyword_scores)

        # Top K ordering
        top_indices = np.argsort(combined_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((float(combined_scores[idx]), self.passages[idx]))

        return results
