"""
Batch export all saved sessions to multiple formats.
Usage: python scripts/export_all.py [--format md|csv|srt|txt|all]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturelens.storage.store import list_sessions, export_markdown
from lecturelens.storage.exports import (
    export_anki_csv, export_srt, export_plain_transcript, export_study_sheet,
)


EXPORTERS = {
    "md": ("Markdown", export_markdown),
    "csv": ("Anki CSV", export_anki_csv),
    "srt": ("SRT Subtitles", export_srt),
    "txt": ("Plain Transcript", export_plain_transcript),
    "study": ("Study Sheet", export_study_sheet),
}


def main():
    parser = argparse.ArgumentParser(description="Batch export all sessions.")
    parser.add_argument(
        "--format", choices=list(EXPORTERS.keys()) + ["all"],
        default="all", help="Export format (default: all)",
    )
    args = parser.parse_args()

    sessions = list_sessions()
    if not sessions:
        print("No saved sessions found.")
        return

    formats = list(EXPORTERS.keys()) if args.format == "all" else [args.format]

    for session in sessions:
        print(f"\n--- {session.metadata.title} ({session.metadata.id[:8]}) ---")
        for fmt in formats:
            label, exporter = EXPORTERS[fmt]
            try:
                path = exporter(session)
                print(f"  [{label}] {path}")
            except Exception as e:
                print(f"  [{label}] ERROR: {e}")

    print(f"\nExported {len(sessions)} sessions in {len(formats)} format(s).")


if __name__ == "__main__":
    main()
