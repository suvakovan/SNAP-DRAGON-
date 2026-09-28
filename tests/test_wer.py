"""
Unit tests for Word Error Rate (WER) calculation and character similarity.
"""

import pytest
from scripts.consistency_check import compute_wer, compute_char_similarity, normalize_text


@pytest.mark.unit
def test_normalize_text():
    assert normalize_text("Hello, World!") == "hello world"
    assert normalize_text("  NPU   acceleration  ") == "npu acceleration"


@pytest.mark.unit
def test_wer_identical_strings():
    ref = "The quick brown fox jumps over the lazy dog"
    hyp = "The quick brown fox jumps over the lazy dog"
    assert compute_wer(ref, hyp) == 0.0


@pytest.mark.unit
def test_wer_substitution():
    ref = "cat sat on mat"
    hyp = "cat sat on hat"  # 1 substitution in 4 words = 0.25
    assert compute_wer(ref, hyp) == 0.25


@pytest.mark.unit
def test_wer_deletion():
    ref = "cat sat on mat"
    hyp = "cat sat mat"     # 1 deletion in 4 words = 0.25
    assert compute_wer(ref, hyp) == 0.25


@pytest.mark.unit
def test_wer_empty():
    assert compute_wer("", "") == 0.0
    assert compute_wer("hello", "") == 1.0


@pytest.mark.unit
def test_char_similarity():
    assert compute_char_similarity("Snapdragon NPU", "snapdragon npu") == 1.0
    assert compute_char_similarity("Snapdragon NPU", "Intel CPU") < 0.5
