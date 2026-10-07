"""
Print project statistics: lines of code, file counts, test counts.
Usage: python scripts/stats.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_lines(filepath: Path) -> int:
    try:
        return len(filepath.read_text(encoding="utf-8").splitlines())
    except Exception:
        return 0


def main():
    src_files = list((ROOT / "lecturelens").rglob("*.py"))
    test_files = list((ROOT / "tests").rglob("*.py"))
    script_files = list((ROOT / "scripts").rglob("*.py"))
    doc_files = list((ROOT / "docs").rglob("*.md"))

    src_lines = sum(count_lines(f) for f in src_files)
    test_lines = sum(count_lines(f) for f in test_files)
    script_lines = sum(count_lines(f) for f in script_files)

    print("=" * 50)
    print("LectureLens Project Statistics")
    print("=" * 50)
    print(f"Source files:    {len(src_files):>4} files, {src_lines:>6} lines")
    print(f"Test files:      {len(test_files):>4} files, {test_lines:>6} lines")
    print(f"Script files:    {len(script_files):>4} files, {script_lines:>6} lines")
    print(f"Doc files:       {len(doc_files):>4} files")
    print(f"{'â”€' * 50}")
    print(f"Total Python:    {len(src_files) + len(test_files) + len(script_files):>4} files, {src_lines + test_lines + script_lines:>6} lines")


if __name__ == "__main__":
    main()
