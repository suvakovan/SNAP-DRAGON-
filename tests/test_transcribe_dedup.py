"""Tests for overlap deduplication in transcription pipeline."""

from lecturelens.pipeline.transcribe import deduplicate_overlap_text


class TestDeduplicateOverlapText:
    def test_no_overlap(self):
        assert deduplicate_overlap_text("hello world", "foo bar") == "foo bar"

    def test_single_word_overlap(self):
        assert deduplicate_overlap_text("the quick brown", "brown fox jumps") == "fox jumps"

    def test_multi_word_overlap(self):
        result = deduplicate_overlap_text("one two three four", "three four five six")
        assert result == "five six"

    def test_empty_prev(self):
        assert deduplicate_overlap_text("", "hello world") == "hello world"

    def test_empty_current(self):
        assert deduplicate_overlap_text("hello", "") == ""

    def test_both_empty(self):
        assert deduplicate_overlap_text("", "") == ""

    def test_identical_texts(self):
        result = deduplicate_overlap_text("a b c", "a b c")
        # Up to 5-word overlap check
        assert result == ""

    def test_no_overlap_different_words(self):
        assert deduplicate_overlap_text("alpha beta", "gamma delta") == "gamma delta"
