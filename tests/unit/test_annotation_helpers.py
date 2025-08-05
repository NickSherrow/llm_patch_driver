from sortedcontainers import SortedDict
import pytest

from llm_patch_driver.driver.annotation_helpers import (
    build_map,
    map_to_annotated_text,
    map_to_original_text,
    build_json_annotation_and_map,
)


SAMPLE_TEXT = "Hello world. How are you?\nAnother line."


# Adjust normalization helper for whitespace differences between original and reconstructed text
_DEF_NORMALIZE_HELPER = lambda s: "".join(s.split())


def test_build_map_and_original_roundtrip():
    """Original text without whitespace differences should be reconstructable."""
    sent_map = build_map(SAMPLE_TEXT)
    reconstructed = map_to_original_text(sent_map)
    assert _DEF_NORMALIZE_HELPER(reconstructed) == _DEF_NORMALIZE_HELPER(SAMPLE_TEXT)


def test_map_to_annotated_text():
    """map_to_annotated_text should include sentence ids and preserve sentence order."""
    sent_map = build_map(SAMPLE_TEXT)
    annotated = map_to_annotated_text(sent_map)
    expected = (
        "<tid=1_1>Hello world.</tid>\n"
        "<tid=1_2>How are you?</tid>\n"
        "<tid=2_1>Another line.</tid>"
    )
    assert annotated == expected


def test_build_json_annotation_and_map():
    data = {"a": 1, "b": {"c": [2, 3]}}

    annotated, attr_map = build_json_annotation_and_map(data)

    # Expected attribute id -> JSON pointer mapping
    expected_attr_map = SortedDict({1: "/a", 2: "/b", 3: "/b/c"})
    assert attr_map == expected_attr_map

    # Expected annotated structure (note that scalar values are kept unmodified)
    expected_annotated = {
        "<a=1 k=a>": 1,
        "<a=2 k=b>": {
            "<a=3 k=c>": [
                "<i=1 v=2>",
                "<i=2 v=3>",
            ]
        },
    }
    assert annotated == expected_annotated