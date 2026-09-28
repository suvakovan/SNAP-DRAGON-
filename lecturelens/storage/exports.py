"""
Study Exports — Anki CSV, SRT subtitles, plain transcript, and Markdown study sheet.
"""

import csv
import json
from pathlib import Path
from typing import Optional

from lecturelens.pipeline.session import LectureSession
from lecturelens.config import config
from lecturelens.logging_setup import logger

_EXPORTS_DIR = config.data_dir / "exports"


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def export_anki_csv(session: LectureSession, output_dir: Optional[Path] = None) -> Path:
    """Exports flashcards as an Anki-compatible CSV (front, back, tags)."""
    out_dir = _ensure_dir(output_dir or _EXPORTS_DIR)
    slug = session.metadata.title.replace(" ", "_")[:40]
    filepath = out_dir / f"{slug}_{session.metadata.id[:8]}_anki.csv"

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for fc in session.flashcards:
            tag = f"LectureLens {session.metadata.title}"
            writer.writerow([fc.question, fc.answer, tag])

    logger.info(f"Anki CSV exported: {filepath}")
    return filepath


def _seconds_to_srt_ts(sec: float) -> str:
    """Converts float seconds to SRT timestamp HH:MM:SS,mmm format."""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def export_srt(session: LectureSession, output_dir: Optional[Path] = None) -> Path:
    """Exports transcript segments as an SRT subtitle file."""
    out_dir = _ensure_dir(output_dir or _EXPORTS_DIR)
    slug = session.metadata.title.replace(" ", "_")[:40]
    filepath = out_dir / f"{slug}_{session.metadata.id[:8]}.srt"

    lines = []
    for i, seg in enumerate(session.segments, 1):
        start_ts = _seconds_to_srt_ts(seg.get("start", 0.0))
        end_ts = _seconds_to_srt_ts(seg.get("end", 0.0))
        text = seg.get("text", "").strip()
        lines.append(f"{i}\n{start_ts} --> {end_ts}\n{text}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"SRT exported: {filepath}")
    return filepath


def export_plain_transcript(session: LectureSession, output_dir: Optional[Path] = None) -> Path:
    """Exports timestamped plain text transcript."""
    out_dir = _ensure_dir(output_dir or _EXPORTS_DIR)
    slug = session.metadata.title.replace(" ", "_")[:40]
    filepath = out_dir / f"{slug}_{session.metadata.id[:8]}_transcript.txt"

    lines = [f"# {session.metadata.title}", f"Date: {session.metadata.created_at[:10]}", ""]
    for seg in session.segments:
        start = seg.get("start", 0.0)
        text = seg.get("text", "").strip()
        lines.append(f"[{start:.1f}s] {text}")

    lines.append("")
    lines.append(f"[Full transcript: {len(session.transcript.split())} words]")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Plain transcript exported: {filepath}")
    return filepath


def export_study_sheet(session: LectureSession, output_dir: Optional[Path] = None) -> Path:
    """Exports a complete Markdown study sheet with summary, key terms, quiz, and flashcards."""
    out_dir = _ensure_dir(output_dir or _EXPORTS_DIR)
    slug = session.metadata.title.replace(" ", "_")[:40]
    filepath = out_dir / f"{slug}_{session.metadata.id[:8]}_study.md"

    md = [f"# {session.metadata.title} — Study Sheet", f"*Generated: {session.metadata.created_at[:10]}*", ""]
    md += ["## Summary", ""]
    for b in session.summary:
        md.append(f"- {b}")
    md += ["", "## Key Terms", ""]
    for k in session.key_terms:
        md.append(f"**{k.term}**: {k.definition}")
    md += ["", "## Revision", "", session.revision_paragraph, ""]
    md += ["## Quiz (with Answer Key)", ""]
    for i, q in enumerate(session.quiz, 1):
        md.append(f"**Q{i}.** {q.question}")
        for j, opt in enumerate(q.options):
            marker = " ✓" if j == q.correct_index else ""
            md.append(f"  {chr(65+j)}. {opt}{marker}")
        md.append(f"  *{q.explanation}*")
        md.append("")
    md += ["## Flashcards", ""]
    for i, fc in enumerate(session.flashcards, 1):
        md.append(f"**{i}. Q:** {fc.question}")
        md.append(f"   **A:** {fc.answer}")
        md.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    logger.info(f"Study sheet exported: {filepath}")
    return filepath
