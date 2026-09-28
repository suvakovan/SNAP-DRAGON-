"""
Output Consistency & Word Error Rate (WER) Evaluation Script.
Compares transcribed text against reference transcripts or across backends.
"""

import re
import sys
import json
import difflib
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def normalize_text(text: str) -> str:
    """Normalizes text by lowercasing, stripping punctuation, and collapsing whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_wer(reference: str, hypothesis: str) -> float:
    """
    Computes Word Error Rate (WER) using Levenshtein distance on normalized word lists.
    WER = (Substitutions + Deletions + Insertions) / Total_Words_in_Reference
    """
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    # Levenshtein distance matrix
    r_len = len(ref_words)
    h_len = len(hyp_words)
    dp = [[0] * (h_len + 1) for _ in range(r_len + 1)]

    for i in range(r_len + 1):
        dp[i][0] = i
    for j in range(h_len + 1):
        dp[0][j] = j

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                substitution = dp[i - 1][j - 1] + 1
                insertion = dp[i][j - 1] + 1
                deletion = dp[i - 1][j] + 1
                dp[i][j] = min(substitution, insertion, deletion)

    edit_distance = dp[r_len][h_len]
    wer = edit_distance / float(r_len)
    return round(wer, 4)


def compute_char_similarity(text1: str, text2: str) -> float:
    """Computes character-level SequenceMatcher similarity ratio (0.0 to 1.0)."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    matcher = difflib.SequenceMatcher(None, norm1, norm2)
    return round(matcher.ratio(), 4)


def run_consistency_evaluation(
    ref_text: str, hyp_text: str, label: str = "Evaluation"
) -> Dict[str, Any]:
    """Runs complete consistency evaluation between reference and hypothesis."""
    wer = compute_wer(ref_text, hyp_text)
    char_sim = compute_char_similarity(ref_text, hyp_text)
    passed = wer <= 0.35

    return {
        "label": label,
        "reference_word_count": len(normalize_text(ref_text).split()),
        "hypothesis_word_count": len(normalize_text(hyp_text).split()),
        "wer": wer,
        "char_similarity": char_sim,
        "passed": passed
    }


if __name__ == "__main__":
    ref = "Snapdragon X Series processors contain dedicated Hexagon NPU hardware designed to accelerate AI workloads."
    hyp = "Snapdragon X Series processors contain dedicated Hexagon NPU hardware designed to accelerate AI workloads."

    res = run_consistency_evaluation(ref, hyp, label="Sanity Check")
    print(json.dumps(res, indent=2))
