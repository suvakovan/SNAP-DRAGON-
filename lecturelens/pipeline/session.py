"""
Session object definition and end-to-end pipeline orchestrator.
"""

import argparse
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

from lecturelens.pipeline.transcribe import transcribe_file, transcribe_audio_array
from lecturelens.pipeline.notes import generate_full_notes, KeyTerm, QuizQuestion, Flashcard
from lecturelens.backends.base import STTResult
from lecturelens.config import config
from lecturelens.logging_setup import logger


class SessionMetadata(BaseModel):
    id: str
    title: str
    created_at: str
    audio_duration_seconds: float
    total_processing_seconds: float
    stt_backend: Dict[str, Any]
    llm_backend: Dict[str, Any]
    embed_backend: Dict[str, Any]


class LectureSession(BaseModel):
    metadata: SessionMetadata
    transcript: str
    segments: List[Dict[str, Any]]
    summary: List[str]
    key_terms: List[KeyTerm]
    revision_paragraph: str
    quiz: List[QuizQuestion]
    flashcards: List[Flashcard]
    timing_metrics: Dict[str, Any]


def run_full_pipeline(
    audio_source: Any,
    title: str = "Untitled Lecture",
    progress_callback: Optional[Callable[[str, float], None]] = None,
    stt_preference: str = "auto",
    llm_preference: str = "auto"
) -> LectureSession:
    """
    Orchestrates full end-to-end execution:
    Audio loading -> STT transcription -> LLM Summarization/Quiz/Flashcards -> Session creation.
    Emits progress callbacks (message, fraction 0.0-1.0).
    """
    start_total = time.time()
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    def update_progress(msg: str, frac: float):
        logger.info(f"Pipeline Progress [{frac * 100:.0f}%]: {msg}")
        if progress_callback:
            progress_callback(msg, frac)

    # Step 1: Speech-to-Text Transcription
    update_progress("Starting Speech-to-Text Transcription...", 0.1)
    if isinstance(audio_source, (str, Path)):
        stt_res, stt_backend = transcribe_file(str(audio_source), backend_preference=stt_preference)
    elif hasattr(audio_source, "dtype"):  # numpy array
        from lecturelens.backends import get_stt_backend
        stt_backend = get_stt_backend(stt_preference)
        stt_res = transcribe_audio_array(audio_source, backend=stt_backend)
    else:
        raise ValueError("Unsupported audio source type.")

    update_progress("Transcription finished. Generating notes & summary...", 0.4)

    # Step 2: Notes, Quiz, and Flashcards Generation
    notes = generate_full_notes(
        stt_res.text if stt_res.text.strip() else "No speech detected in audio clip.",
        backend_preference=llm_preference
    )

    update_progress("Notes generated. Finalizing session store...", 0.8)

    # Step 3: Metadata & Metrics Assembly
    total_processing_time = round(time.time() - start_total, 2)

    metadata = SessionMetadata(
        id=session_id,
        title=title,
        created_at=created_at,
        audio_duration_seconds=round(stt_res.audio_seconds, 2),
        total_processing_seconds=total_processing_time,
        stt_backend={
            "device": stt_backend.info.device,
            "verified_npu": stt_backend.info.verified_npu,
            "runtime": stt_backend.info.runtime,
            "name": stt_backend.info.name
        },
        llm_backend=notes.llm_metrics,
        embed_backend={"device": "CPU", "verified_npu": False, "name": config.embed_model_name}
    )

    session = LectureSession(
        metadata=metadata,
        transcript=stt_res.text,
        segments=stt_res.segments,
        summary=notes.summary,
        key_terms=notes.key_terms,
        revision_paragraph=notes.revision_paragraph,
        quiz=notes.quiz,
        flashcards=notes.flashcards,
        timing_metrics={
            "stt_wall_seconds": round(stt_res.wall_seconds, 2),
            "stt_rtf": round(stt_res.rtf, 4),
            "total_pipeline_seconds": total_processing_time
        }
    )

    update_progress("Pipeline execution complete!", 1.0)

    # Automatically save session
    from lecturelens.storage.store import save_session
    save_session(session)

    return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full LectureLens pipeline on an audio file.")
    parser.add_argument("--file", type=str, required=True, help="Input audio file path")
    parser.add_argument("--title", type=str, default="Sample Lecture", help="Session title")
    args = parser.parse_args()

    session = run_full_pipeline(args.file, title=args.title)
    from lecturelens.storage.store import export_markdown
    md_path = export_markdown(session)
    print(f"\nPipeline completed! Session ID: {session.metadata.id}")
    print(f"Exported Markdown notes to: {md_path}")
