from sortedcontainers import SortedDict
import pytest
import json

from llm_patch_driver.patch.string.string_patch import StrPatch
from llm_patch_driver.patch.json.json_patch import JsonPatch


SAMPLE_TEXT = "Hello world. How are you?\nAnother line."

def test_build_map_and_original_roundtrip():
    """Original text without whitespace differences should be reconstructable."""
    sent_map = StrPatch.build_map(SAMPLE_TEXT)
    reconstructed = StrPatch.content_from_map(SAMPLE_TEXT, sent_map)
    assert reconstructed == SAMPLE_TEXT


def test_map_to_annotated_text():
    """map_to_annotated_text should include sentence ids and preserve sentence order."""
    sent_map = StrPatch.build_map(SAMPLE_TEXT)
    annotated = StrPatch.build_annotation(SAMPLE_TEXT, sent_map)
    expected = (
        "<tid=1_1>Hello world.</tid>\n"
        "<tid=1_2>How are you?</tid>\n"
        "<tid=2_1>Another line.</tid>"
    )
    assert annotated == expected


def test_build_json_annotation_and_map():
    data = {"a": 1, "b": {"c": [2, 3]}}
    attr_map = JsonPatch.build_map(data)
    annotated = JsonPatch.build_annotation(data, attr_map)

    # Expected attribute id -> JSON pointer mapping
    expected_attr_map = SortedDict({1: "/a", 2: "/b", 3: "/b/c"})
    assert attr_map == expected_attr_map

    # Expected annotated JSON string (top-level should be a formatted string)
    expected_annotated_struct = {
        "<a=1 k=a>": 1,
        "<a=2 k=b>": {
            "<a=3 k=c>": [
                "<i=1 v=2>",
                "<i=2 v=3>",
            ]
        },
    }
    expected_annotated = json.dumps(expected_annotated_struct, indent=4, ensure_ascii=False)
    assert annotated == expected_annotated