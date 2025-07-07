import pytest
from llm_patch_driver.patch_schemas.string_patch import StrPatch, ReplaceOp, DeleteOp, InsertAfterOp


def test_parse_tids_valid():
    patch = StrPatch(tids=["1_1", "2_3"], operation=ReplaceOp(pattern="foo", replacement="bar"))
    assert patch._parsed_tids == [(1, 1), (2, 3)]


def test_parse_tids_invalid():
    with pytest.raises(ValueError):
        StrPatch(tids=["bad"], operation=DeleteOp())
