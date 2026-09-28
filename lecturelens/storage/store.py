"""
Storage engine for loading, saving, listing, deleting, and exporting LectureLens sessions.
"""

import json
from pathlib import Path
from typing import List, Optional
from lecturelens.config import config
from lecturelens.pipeline.session import LectureSession
from lecturelens.logging_setup import logger


def save_session(session: LectureSession) -> Path:
    """Saves session object as JSON file in sessions_dir."""
    config.sessions_dir.mkdir(parents=True, exist_ok=True)
    filepath = config.sessions_dir / f"{session.metadata.id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session.model_dump(), f, indent=2)
    logger.info(f"Saved session {session.metadata.id} to {filepath}")
    return filepath


def load_session(session_id: str) -> Optional[LectureSession]:
    """Loads a session object from JSON file by ID."""
    filepath = config.sessions_dir / f"{session_id}.json"
    if not filepath.exists():
        logger.warning(f"Session file not found: {filepath}")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LectureSession(**data)
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {e}")
        return None


def list_sessions() -> List[LectureSession]:
    """Lists all saved sessions sorted by created_at descending."""
    config.sessions_dir.mkdir(parents=True, exist_ok=True)
    sessions: List[LectureSession] = []
    for p in config.sessions_dir.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append(LectureSession(**data))
        except Exception as e:
            logger.warning(f"Error reading session file {p}: {e}")

    sessions.sort(key=lambda s: s.metadata.created_at, reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Deletes a session file by ID."""
    filepath = config.sessions_dir / f"{session_id}.json"
    if filepath.exists():
        filepath.unlink()
        logger.info(f"Deleted session {session_id}")
        return True
    return False


def export_markdown(session: LectureSession, output_dir: Optional[Path] = None) -> Path:
    """Exports lecture session into a clean, formatted Markdown document."""
    if output_dir is None:
        output_dir = config.data_dir / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{session.metadata.title.replace(' ', '_')}_{session.metadata.id[:8]}.md"

    md_content = f"# {session.metadata.title}\n\n"
    md_content += f"**Date:** {session.metadata.created_at[:10]} | **Audio Duration:** {session.metadata.audio_duration_seconds:.1f}s | **Processing Backend:** {session.metadata.stt_backend.get('device', 'CPU')}\n\n"
    md_content += "---\n\n"

    md_content += "## Executive Summary\n\n"
    for bullet in session.summary:
        md_content += f"- {bullet}\n"
    md_content += "\n"

    md_content += "## Essential Key Terms\n\n"
    for term in session.key_terms:
        md_content += f"- **{term.term}**: {term.definition}\n"
    md_content += "\n"

    md_content += "## Revision Plan\n\n"
    md_content += f"{session.revision_paragraph}\n\n"

    md_content += "## Multiple Choice Quiz\n\n"
    for idx, q in enumerate(session.quiz, 1):
        md_content += f"### Q{idx}. {q.question}\n"
        for o_idx, opt in enumerate(q.options):
            marker = "(Correct)" if o_idx == q.correct_index else ""
            md_content += f"- {'ABCD'[o_idx]}. {opt} {marker}\n"
        md_content += f"*Explanation:* {q.explanation}\n\n"

    md_content += "## Flashcards\n\n"
    for idx, fc in enumerate(session.flashcards, 1):
        md_content += f"**Card {idx}**\n"
        md_content += f"- **Front:** {fc.question}\n"
        md_content += f"- **Back:** {fc.answer}\n\n"

    md_content += "## Full Transcript\n\n"
    md_content += f"{session.transcript}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info(f"Exported session Markdown to {filepath}")
    return filepath
