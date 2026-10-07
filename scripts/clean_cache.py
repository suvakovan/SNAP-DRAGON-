"""
Clean Python cache files and temporary artifacts.
Usage: python scripts/clean_cache.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ["__pycache__", ".pytest_cache", "*.pyc", "*.pyo"]


def clean():
    removed = 0
    for pattern in ["__pycache__", ".pytest_cache"]:
        for d in ROOT.rglob(pattern):
            if d.is_dir() and ".venv" not in str(d):
                shutil.rmtree(d, ignore_errors=True)
                print(f"  Removed: {d.relative_to(ROOT)}")
                removed += 1

    for pattern in ["*.pyc", "*.pyo"]:
        for f in ROOT.rglob(pattern):
            if ".venv" not in str(f):
                f.unlink(missing_ok=True)
                removed += 1

    # Clean temp files
    for f in ROOT.glob("tmp_*.py"):
        f.unlink(missing_ok=True)
        print(f"  Removed: {f.name}")
        removed += 1

    for f in ROOT.glob("tmp_*.txt"):
        f.unlink(missing_ok=True)
        print(f"  Removed: {f.name}")
        removed += 1

    print(f"\nCleaned {removed} cache items.")


if __name__ == "__main__":
    clean()
