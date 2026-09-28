"""
Tests for grounded Q&A citation parser.
"""

import pytest
from lecturelens.pipeline.qa import parse_citations, build_qa_context


@pytest.mark.unit
def test_parse_citations_valid():
    answer = "According to [1] and [3], the NPU accelerates inference."
    cites = parse_citations(answer, num_passages=4)
    assert 1 in cites
    assert 3 in cites


@pytest.mark.unit
def test_parse_citations_out_of_range():
    """Citations beyond num_passages should be discarded."""
    answer = "See [5] and [1]."
    cites = parse_citations(answer, num_passages=3)
    assert 5 not in cites
    assert 1 in cites


@pytest.mark.unit
def test_build_qa_context_format():
    passages = [
        (0.95, {"timestamp_sec": 12.0, "text": "NPUs accelerate matrix operations."}),
        (0.80, {"timestamp_sec": 45.0, "text": "Whisper runs faster on HTP."})
    ]
    ctx = build_qa_context(passages)
    assert "[1] (at 12.0s)" in ctx
    assert "[2] (at 45.0s)" in ctx
