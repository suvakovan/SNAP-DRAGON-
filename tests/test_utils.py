"""Tests for utility functions."""

from lecturelens.utils import truncate_text, format_duration, safe_filename


class TestTruncateText:
    def test_short_text(self):
        assert truncate_text("hello world", 10) == "hello world"

    def test_long_text(self):
        result = truncate_text("one two three four five", 3)
        assert result == "one two three..."

    def test_empty_text(self):
        assert truncate_text("", 5) == ""


class TestFormatDuration:
    def test_seconds(self):
        assert format_duration(45.3) == "45.3s"

    def test_minutes(self):
        assert format_duration(125.0) == "2m 5s"

    def test_hours(self):
        assert format_duration(3725.0) == "1h 2m 5s"


class TestSafeFilename:
    def test_clean_title(self):
        assert safe_filename("My Lecture") == "My_Lecture"

    def test_special_chars(self):
        result = safe_filename("Lecture: NPU & GPU (2026)")
        assert ":" not in result
        assert "&" not in result

    def test_max_length(self):
        result = safe_filename("A" * 100, max_length=50)
        assert len(result) <= 50
