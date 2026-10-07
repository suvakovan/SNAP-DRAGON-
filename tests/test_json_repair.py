"""Tests for JSON cleaning and repair utility in notes pipeline."""

import pytest
from lecturelens.pipeline.notes import clean_and_parse_json


class TestCleanAndParseJSON:
    def test_valid_json(self):
        assert clean_and_parse_json('{"key": "value"}') == {"key": "value"}

    def test_markdown_code_block(self):
        raw = '```json\n{"key": "value"}\n```'
        assert clean_and_parse_json(raw) == {"key": "value"}

    def test_trailing_comma_object(self):
        raw = '{"key": "value",}'
        assert clean_and_parse_json(raw) == {"key": "value"}

    def test_trailing_comma_array(self):
        raw = '{"items": ["a", "b",]}'
        assert clean_and_parse_json(raw) == {"items": ["a", "b"]}

    def test_smart_quotes(self):
        raw = '{\u201ckey\u201d: \u201cvalue\u201d}'
        assert clean_and_parse_json(raw)["key"] == "value"

    def test_preamble_text(self):
        raw = 'Here is the JSON:\n{"key": "value"}\nEnd of response.'
        assert clean_and_parse_json(raw) == {"key": "value"}

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            clean_and_parse_json("this is not json at all")

    def test_nested_object(self):
        raw = '{"outer": {"inner": [1, 2, 3]}}'
        result = clean_and_parse_json(raw)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_empty_object(self):
        assert clean_and_parse_json("{}") == {}

    def test_array_input(self):
        raw = '[{"a": 1}, {"b": 2}]'
        result = clean_and_parse_json(raw)
        assert len(result) == 2
