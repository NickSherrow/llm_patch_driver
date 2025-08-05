from __future__ import annotations

"""Test suite for the `StrPatch` schema and its integration with `PatchDriver`.

This covers three areas:

1. Deserialisation from a JSON string into a valid `StrPatch` instance.
2. Validation errors when the JSON input is invalid.
3. End-to-end application of a string patch via `PatchDriver` to ensure the
   underlying text is correctly modified.
"""

from copy import deepcopy
import json
import asyncio

import pytest
from pydantic import ValidationError

from llm_patch_driver.patch_schemas.string_patch import StrPatch, ReplaceOp, DeleteOp, InsertAfterOp
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.driver.driver import PatchDriver
from typing import cast

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_text() -> str:
    """Provide sample multi-line text for testing."""

    # Two short sentences split across two lines to make TID mapping obvious.
    return "Hello world.\nThis is a test."


@pytest.fixture()
def patch_driver(sample_text: str) -> PatchDriver[str]:
    """Initialise a `PatchDriver` in string-patch mode for *sample_text*."""

    # No validation schema ⇒ driver enters StrPatch pathway.
    target = PatchTarget[str](object=deepcopy(sample_text))
    return PatchDriver(target)


# ---------------------------------------------------------------------------
# Deserialisation tests
# ---------------------------------------------------------------------------


def test_str_patch_deserialization_valid():
    """A valid JSON string should deserialise into a `StrPatch`."""

    json_str = json.dumps(
        {
            "tids": ["1_1"],
            "operation": {"type": "replace", "pattern": "world", "replacement": "ChatGPT"},
        }
    )

    patch = StrPatch.model_validate_json(json_str)

    assert isinstance(patch, StrPatch)
    assert patch.tids == ["1_1"]
    assert isinstance(patch.operation, ReplaceOp)
    assert patch.operation.pattern == "world"
    assert patch.operation.replacement == "ChatGPT"



def test_str_patch_deserialization_invalid():
    """Invalid JSON input should raise a *ValidationError* (wrapped ValueError)."""

    # Missing required "replacement" field for a replace operation.
    json_str = json.dumps(
        {
            "tids": ["1_1"],
            "operation": {"type": "replace", "pattern": "world"},
        }
    )

    with pytest.raises((ValidationError, ValueError)):
        StrPatch.model_validate_json(json_str)


# ---------------------------------------------------------------------------
# Patch application test via `PatchDriver`
# ---------------------------------------------------------------------------


def test_apply_replace_patch(patch_driver: PatchDriver[str]):
    """Applying a simple replace patch should update the text content."""

    patch = StrPatch(
        tids=["1_1"],
        operation=ReplaceOp(pattern="world", replacement="ChatGPT"),
    )

    bundle = patch_driver.patch_schema(patches=[patch])

    # `apply_patch_bundle` is async → run in event loop.
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    expected_text = "Hello ChatGPT.\nThis is a test."
    assert patch_driver.patched_content == expected_text


# ---------------------------------------------------------------------------
# Additional Patch operation tests
# ---------------------------------------------------------------------------



def test_apply_delete_patch(patch_driver: PatchDriver[str]):
    """Deleting a sentence should remove the corresponding line from the text."""

    # Delete the first (and only) sentence of the first line.
    patch = StrPatch(
        tids=["1_1"],
        operation=DeleteOp(),
    )

    bundle = patch_driver.patch_schema(patches=[patch])  # type: ignore[arg-type]
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    expected_text = "This is a test."
    assert patch_driver.patched_content == expected_text



def test_apply_insert_after_patch(patch_driver: PatchDriver[str]):
    """Inserting text after a given line should shift subsequent lines down."""

    patch = StrPatch(
        tids=["1_1"],
        operation=InsertAfterOp(text="New line."),
    )

    bundle = patch_driver.patch_schema(patches=[patch])  # type: ignore[arg-type]
    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    expected_text = "Hello world.\nNew line.\nThis is a test."
    assert patch_driver.patched_content == expected_text



def test_apply_multiple_patches_bundle(patch_driver: PatchDriver[str]):
    """Applying a bundle containing multiple patch types should yield the correct final text.

    The patches are intentionally provided in a non-optimal order to ensure that
    ``StrPatch.bundle_builder`` reorders them (replace → delete → insert).
    """

    patch_replace = StrPatch(
        tids=["1_1"],
        operation=ReplaceOp(pattern="Hello", replacement="Hi"),
    )

    patch_delete = StrPatch(
        tids=["2_1"],
        operation=DeleteOp(),
    )

    patch_insert = StrPatch(
        tids=["1_1"],
        operation=InsertAfterOp(text="New line."),
    )

    # Provide patches in reverse priority order to test internal sorting.
    patches = [patch_insert, patch_delete, patch_replace]

    bundle = patch_driver.patch_schema(patches=patches)  # type: ignore[arg-type]

    # Ensure bundle_builder sorted patches correctly.
    first_patch = cast(StrPatch, bundle.patches[0])
    second_patch = cast(StrPatch, bundle.patches[1])
    third_patch = cast(StrPatch, bundle.patches[2])

    assert isinstance(first_patch.operation, ReplaceOp)
    assert isinstance(second_patch.operation, DeleteOp)
    assert isinstance(third_patch.operation, InsertAfterOp)

    asyncio.run(patch_driver.apply_patch_bundle(bundle))

    expected_text = "Hi world.\nNew line."
    assert patch_driver.patched_content == expected_text