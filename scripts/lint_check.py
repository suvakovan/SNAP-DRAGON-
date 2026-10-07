"""
Quick lint check using built-in ast and py_compile.
Usage: python scripts/lint_check.py
"""

import ast
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_syntax(filepath: Path) -> bool:
    try:
        source = filepath.read_text(encoding="utf-8")
        ast.parse(source, filename=str(filepath))
        return True
    except SyntaxError as e:
        print(f"  [SYNTAX ERROR] {filepath.relative_to(ROOT)}: {e}")
        return False


def main():
    py_files = list((ROOT / "lecturelens").rglob("*.py"))
    py_files += list((ROOT / "tests").rglob("*.py"))
    py_files += list((ROOT / "scripts").rglob("*.py"))

    errors = 0
    for f in py_files:
        if ".venv" in str(f) or "__pycache__" in str(f):
            continue
        if not check_syntax(f):
            errors += 1

    if errors == 0:
        print(f"All {len(py_files)} Python files pass syntax check.")
    else:
        print(f"\n{errors} file(s) have syntax errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
