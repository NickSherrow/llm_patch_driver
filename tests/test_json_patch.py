import pytest
from llm_patch_driver.patch_schemas.json_patch import JsonPatch


def test_json_patch_valid():
    patch = JsonPatch(op="add", a_id=1, i_id=1, value="x")
    assert patch.op == "add"
    assert patch.a_id == 1


def test_json_patch_invalid_remove_with_value():
    with pytest.raises(ValueError):
        JsonPatch(op="remove", a_id=1, value="x")


def test_json_patch_invalid_replace_with_index():
    with pytest.raises(ValueError):
        JsonPatch(op="replace", a_id=1, i_id=1, value="x")
