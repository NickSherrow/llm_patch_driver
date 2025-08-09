import json
from copy import deepcopy

import pytest
import asyncio
from pydantic import ValidationError

from llm_patch_driver.patch.json.json_patch import JsonPatch
from llm_patch_driver.patch_target.target import PatchTarget
from pydantic import BaseModel, RootModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class DummySchema(RootModel[dict]):
    """A permissive schema that accepts any JSON document.

    PatchDriver switches to JsonPatch mode only when a ``validation_schema``
    is supplied. We provide a dummy schema that will always validate so that
    we can exercise JsonPatch behaviour without constraining the test data.
    """

    root: dict


def _get_a_id(target_lookup_map, json_pointer: str) -> int:
    """Return attribute id (``a_id``) from target's internal map for a pointer."""

    for a_id, pointer in target_lookup_map.items():  # pylint: disable=protected-access
        if pointer == json_pointer:
            return a_id
    raise KeyError(
        f"Could not find pointer {json_pointer} in target's map: {target_lookup_map}"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()

def sample_json():
    """Provide a fresh copy of the JSON document for every test."""

    return {
        "name": "Alice",
        "details": {
            "city": "Wonderland",
            "hobbies": ["reading", "chess"],
        },
    }


@pytest.fixture()

def json_lookup_map(sample_json):
    """Build a lookup map for the sample JSON without constructing `PatchTarget`."""
    return JsonPatch.build_map(sample_json)


# ---------------------------------------------------------------------------
# Deserialisation tests
# ---------------------------------------------------------------------------

def test_json_patch_deserialization_valid():
    """A valid JSON string is successfully deserialised into a JsonPatch."""

    json_str = json.dumps({"op": "replace", "a_id": 1, "value": "Bob"})
    patch = JsonPatch.model_validate_json(json_str)

    assert isinstance(patch, JsonPatch)
    assert patch.op == "replace"
    assert patch.a_id == 1
    assert patch.value == "Bob"


def test_json_patch_deserialization_invalid():
    """An invalid JSON Patch raises *ValidationError* (wrapped ValueError)."""

    # missing required ``value`` for a replace operation
    json_str = json.dumps({"op": "replace", "a_id": 1})
    with pytest.raises((ValidationError, ValueError)):
        JsonPatch.model_validate_json(json_str)


# ---------------------------------------------------------------------------
# Patch application tests via PatchDriver
# ---------------------------------------------------------------------------

def test_replace_root_value(json_lookup_map, sample_json):
    """Replacing a top-level scalar value works."""

    name_id = _get_a_id(json_lookup_map, "/name")
    patch = JsonPatch(op="replace", a_id=name_id, i_id=None, value="Bob")
    dummy_target = type("T", (), {"content": deepcopy(sample_json), "_lookup_map": json_lookup_map})()
    patch.apply_patch(dummy_target)  # type: ignore[arg-type]
    assert dummy_target.content["name"] == "Bob" # type: ignore[attr-defined]


def test_add_list_element(json_lookup_map, sample_json):
    """Adding a new element to an array appends the value at the correct index."""

    hobbies_id = _get_a_id(json_lookup_map, "/details/hobbies")
    # existing list has 2 items – use index 3 (1-based) to append at the end
    patch = JsonPatch(op="add", a_id=hobbies_id, i_id=3, value="painting")

    dummy_target = type("T", (), {"content": deepcopy(sample_json), "_lookup_map": json_lookup_map})()
    patch.apply_patch(dummy_target)  # type: ignore[arg-type]
    assert dummy_target.content["details"]["hobbies"] == [ # type: ignore[attr-defined]
        "reading",
        "chess",
        "painting", 
    ] 


def test_remove_object_key(json_lookup_map, sample_json):
    """Removing a nested object attribute deletes the key."""

    city_id = _get_a_id(json_lookup_map, "/details/city")
    patch = JsonPatch(op="remove", a_id=city_id, i_id=None, value=None)
    dummy_target = type("T", (), {"content": deepcopy(sample_json), "_lookup_map": json_lookup_map})()
    patch.apply_patch(dummy_target)  # type: ignore[arg-type]
    assert "city" not in dummy_target.content["details"] # type: ignore[attr-defined]


def test_remove_list_element(json_lookup_map, sample_json):
    """Removing an element from a list updates the array correctly."""

    hobbies_id = _get_a_id(json_lookup_map, "/details/hobbies")
    # remove first element (index 1 -> underlying json pointer index 0)
    patch = JsonPatch(op="remove", a_id=hobbies_id, i_id=1, value=None)

    dummy_target = type("T", (), {"content": deepcopy(sample_json), "_lookup_map": json_lookup_map})()
    patch.apply_patch(dummy_target)  # type: ignore[arg-type]
    assert dummy_target.content["details"]["hobbies"] == ["chess"] # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Bundle tests – multiple JsonPatch operations
# ---------------------------------------------------------------------------


def test_apply_multiple_json_patches_bundle(json_lookup_map, sample_json):
    """Applying several JsonPatch operations in a single bundle should yield the expected final state."""

    # Helper IDs for the JSON pointers we want to modify.
    name_id = _get_a_id(json_lookup_map, "/name")
    hobbies_id = _get_a_id(json_lookup_map, "/details/hobbies")
    city_id = _get_a_id(json_lookup_map, "/details/city")

    patch_replace_name = JsonPatch(op="replace", a_id=name_id, i_id=None, value="Bob")
    patch_add_hobby = JsonPatch(op="add", a_id=hobbies_id, i_id=3, value="painting")
    patch_remove_city = JsonPatch(op="remove", a_id=city_id, i_id=None, value=None)

    # Provide patches in arbitrary order – JsonPatch.bundle_builder currently
    # preserves order, but the operations are independent so order should not
    # affect the final outcome.
    dummy_target = type("T", (), {"content": deepcopy(sample_json), "_lookup_map": json_lookup_map})()
    for p in [patch_remove_city, patch_add_hobby, patch_replace_name]:
        p.apply_patch(dummy_target)  # type: ignore[arg-type]

    expected_result = {
        "name": "Bob",
        "details": {
            "hobbies": ["reading", "chess", "painting"],
        },
    }

    assert dummy_target.content == expected_result # type: ignore[attr-defined]