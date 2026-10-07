"""
Verify all required Python packages are importable.
Usage: python scripts/check_imports.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REQUIRED = [
    ("numpy", "numpy"),
    ("soundfile", "soundfile"),
    ("sounddevice", "sounddevice"),
    ("streamlit", "streamlit"),
    ("onnxruntime", "onnxruntime"),
    ("pytest", "pytest"),
    ("psutil", "psutil"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
    ("tqdm", "tqdm"),
    ("pydantic", "pydantic"),
    ("pydantic_settings", "pydantic-settings"),
    ("rich", "rich"),
    ("scipy", "scipy"),
    ("requests", "requests"),
    ("dotenv", "python-dotenv"),
    ("tabulate", "tabulate"),
]


def check():
    passed = 0
    failed = 0
    for module, package in REQUIRED:
        try:
            __import__(module)
            print(f"  [OK]   {package}")
            passed += 1
        except ImportError:
            print(f"  [MISS] {package} â€” pip install {package}")
            failed += 1

    print(f"\nResults: {passed} available, {failed} missing.")
    return failed == 0


if __name__ == "__main__":
    success = check()
    sys.exit(0 if success else 1)
