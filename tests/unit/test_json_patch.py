import json
from copy import deepcopy

import pytest
import asyncio
from pydantic import ValidationError

from llm_patch_driver.patch_schemas.json_patch import JsonPatch
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.driver.driver import PatchDriver
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


def _get_a_id(driver: PatchDriver, json_pointer: str) -> int:
    """Return attribute id (``a_id``) from driver's internal map for a pointer."""

    for a_id, pointer in driver._map.items():  # pylint: disable=protected-access
        if pointer == json_pointer:
            return a_id
    raise KeyError(f"Could not find pointer {json_pointer} in driver's map: {driver._map}")


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

def patch_driver(sample_json):
    """Return a PatchDriver initialised in JsonPatch mode for *sample_json*."""

    target = PatchTarget[dict](
        object=deepcopy(sample_json),
        validation_schema=DummySchema,  # triggers JsonPatch pathway
    )
    return PatchDriver(target)


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

def test_replace_root_value(patch_driver):
    """Replacing a top-level scalar value works."""

    name_id = _get_a_id(patch_driver, "/name")
    patch = JsonPatch(op="replace", a_id=name_id, i_id=None, value="Bob")

    bundle = patch_driver.patch_schema(patches=[patch])
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    assert patch_driver.patched_object["name"] == "Bob"


def test_add_list_element(patch_driver):
    """Adding a new element to an array appends the value at the correct index."""

    hobbies_id = _get_a_id(patch_driver, "/details/hobbies")
    # existing list has 2 items – use index 3 (1-based) to append at the end
    patch = JsonPatch(op="add", a_id=hobbies_id, i_id=3, value="painting")

    bundle = patch_driver.patch_schema(patches=[patch])
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    assert patch_driver.patched_object["details"]["hobbies"] == [
        "reading",
        "chess",
        "painting",
    ]


def test_remove_object_key(patch_driver):
    """Removing a nested object attribute deletes the key."""

    city_id = _get_a_id(patch_driver, "/details/city")
    patch = JsonPatch(op="remove", a_id=city_id, i_id=None, value=None)

    bundle = patch_driver.patch_schema(patches=[patch])
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    assert "city" not in patch_driver.patched_object["details"]


def test_remove_list_element(patch_driver):
    """Removing an element from a list updates the array correctly."""

    hobbies_id = _get_a_id(patch_driver, "/details/hobbies")
    # remove first element (index 1 -> underlying json pointer index 0)
    patch = JsonPatch(op="remove", a_id=hobbies_id, i_id=1, value=None)

    bundle = patch_driver.patch_schema(patches=[patch])
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    assert patch_driver.patched_object["details"]["hobbies"] == ["chess"]


# ---------------------------------------------------------------------------
# Bundle tests – multiple JsonPatch operations
# ---------------------------------------------------------------------------


def test_apply_multiple_json_patches_bundle(patch_driver):
    """Applying several JsonPatch operations in a single bundle should yield the expected final state."""

    # Helper IDs for the JSON pointers we want to modify.
    name_id = _get_a_id(patch_driver, "/name")
    hobbies_id = _get_a_id(patch_driver, "/details/hobbies")
    city_id = _get_a_id(patch_driver, "/details/city")

    patch_replace_name = JsonPatch(op="replace", a_id=name_id, i_id=None, value="Bob")
    patch_add_hobby = JsonPatch(op="add", a_id=hobbies_id, i_id=3, value="painting")
    patch_remove_city = JsonPatch(op="remove", a_id=city_id, i_id=None, value=None)

    # Provide patches in arbitrary order – JsonPatch.bundle_builder currently
    # preserves order, but the operations are independent so order should not
    # affect the final outcome.
    bundle = patch_driver.patch_schema(
        patches=[patch_remove_city, patch_add_hobby, patch_replace_name]  # type: ignore[arg-type]
    )

    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    expected_result = {
        "name": "Bob",
        "details": {
            "hobbies": ["reading", "chess", "painting"],
        },
    }

    assert patch_driver.patched_object == expected_result