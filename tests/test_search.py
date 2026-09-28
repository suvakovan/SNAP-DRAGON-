"""
Tests for semantic and hybrid search pipeline.
"""

from lecturelens.pipeline.session import LectureSession, SessionMetadata
from lecturelens.pipeline.search import SearchIndex, chunk_transcript_into_passages


def create_mock_session(session_id: str, title: str, transcript: str) -> LectureSession:
    return LectureSession(
        metadata=SessionMetadata(
            id=session_id,
            title=title,
            created_at="2026-09-28T12:00:00",
            audio_duration_seconds=30.0,
            total_processing_seconds=1.0,
            stt_backend={"device": "CPU"},
            llm_backend={"device": "CPU"},
            embed_backend={"device": "CPU"}
        ),
        transcript=transcript,
        segments=[],
        summary=["Summary bullet"],
        key_terms=[],
        revision_paragraph="Revision paragraph.",
        quiz=[],
        flashcards=[],
        timing_metrics={}
    )


def test_chunk_transcript_into_passages():
    s = create_mock_session("s1", "Physics 101", "Quantum mechanics explores energy quantization and subatomic particles.")
    passages = chunk_transcript_into_passages(s, passage_word_count=5)
    assert len(passages) >= 1
    assert passages[0]["session_title"] == "Physics 101"


def test_search_index_top_k():
    s1 = create_mock_session("s1", "Hardware Lecture", "Snapdragon NPU accelerates AI models locally with low energy.")
    s2 = create_mock_session("s2", "Organic Chemistry", "Photosynthesis converts sunlight into chemical energy in plants.")

    index = SearchIndex()
    index.build_index([s1, s2])

    results = index.search("Snapdragon NPU hardware", top_k=2)
    assert len(results) > 0
    # Top result should be hardware lecture passage
    top_score, top_passage = results[0]
    assert top_passage["session_title"] == "Hardware Lecture"
