"""
Claims checker: extracts all concrete metric numbers from docs and README,
then checks each against files in benchmarks/results/ or docs/HEADLINE_RESULTS.md.
Reports orphan numbers (in docs but no backing evidence file).
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# Files to scan for claims
CLAIM_FILES = [
    root / "README.md",
    root / "docs" / "HEADLINE_RESULTS.md",
    root / "docs" / "SUBMISSION_FORM_DRAFT.md",
]

# Evidence files (benchmarks/results/ + HEADLINE_RESULTS itself)
EVIDENCE_FILES = list((root / "benchmarks" / "results").glob("*.json")) + \
                 list((root / "benchmarks" / "results").glob("*.csv")) + \
                 [root / "docs" / "HEADLINE_RESULTS.md",
                  root / "docs" / "AUDIT_REPORT.md",
                  root / "actual_transcript.txt"]

# Load all evidence text
evidence_text = ""
for ef in EVIDENCE_FILES:
    if ef.exists():
        try:
            evidence_text += ef.read_text(encoding="utf-8", errors="ignore") + "\n"
        except Exception:
            pass

# Pattern: extract numbers with units from claim files
NUMBER_PATTERN = re.compile(
    r"([\d]+\.[\d]+|[\d]+)\s*(tok/sec|tok/s|tokens/sec|tokens/s|%|WER|ms|RTF|s\b|x\b)"
)

orphans = []
checked = []

for cf in CLAIM_FILES:
    if not cf.exists():
        continue
    text = cf.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        matches = NUMBER_PATTERN.findall(line)
        for num, unit in matches:
            claim = f"{num}{unit}"
            # Check if core number appears in any evidence file
            found = num in evidence_text
            checked.append((cf.name, line.strip()[:100], claim, found))
            if not found:
                orphans.append((cf.name, line.strip()[:100], claim))

print(f"\n{'='*60}")
print(f"CLAIMS CHECK — {len(checked)} claims scanned")
print(f"{'='*60}")

if orphans:
    print(f"\n⚠  {len(orphans)} ORPHAN NUMBERS (in docs but NOT in any evidence file):")
    for fname, line, claim in orphans:
        print(f"  [{fname}] {claim!r:12s} | {line}")
else:
    print("\n✅ No orphan numbers found — all metrics traceable to an evidence file.")

print(f"\n{'='*60}\n")
