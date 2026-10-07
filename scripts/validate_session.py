"""
Validate saved session JSON files against Pydantic schemas.
Usage: python scripts/validate_session.py [--all | --id SESSION_ID]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturelens.config import config
from lecturelens.pipeline.session import LectureSession


def validate_session_file(filepath: Path) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = LectureSession(**data)
        print(f"  [PASS] {filepath.name} â€” {session.metadata.title}")
        return True
    except Exception as e:
        print(f"  [FAIL] {filepath.name} â€” {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate session JSON files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Validate all sessions")
    group.add_argument("--id", type=str, help="Validate specific session by ID")
    args = parser.parse_args()

    sessions_dir = config.sessions_dir
    if not sessions_dir.exists():
        print("No sessions directory found.")
        return

    if args.all:
        files = list(sessions_dir.glob("*.json"))
        if not files:
            print("No session files found.")
            return
        passed = sum(1 for f in files if validate_session_file(f))
        print(f"\nResults: {passed}/{len(files)} sessions valid.")
    else:
        fp = sessions_dir / f"{args.id}.json"
        if not fp.exists():
            print(f"Session file not found: {fp}")
            sys.exit(1)
        if not validate_session_file(fp):
            sys.exit(1)


if __name__ == "__main__":
    main()
