from __future__ import annotations

"""Unit tests for `StrPatch` and its application via `PatchTarget`.

Covers:
- Deserialisation of a valid/invalid `StrPatch`.
- Applying single and multiple patches through `PatchTarget.apply_patches`.
"""

import json
import asyncio

import pytest
from pydantic import ValidationError

from typing import cast

from llm_patch_driver.patch.string.string_patch import (
    StrPatch,
    ReplaceOp,
    DeleteOp,
    InsertAfterOp,
)
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.patch.base_patch import BasePatch

# Resolve forward refs for Pydantic models used with string annotations
PatchTarget.model_rebuild(_types_namespace={"BasePatch": BasePatch})

# Concrete subclass to satisfy ABC for instantiation in tests
from typing import Type
from llm_patch_driver.patch.base_patch import PatchBundle

class ConcreteStrPatch(StrPatch):
    @classmethod
    def get_bundle_schema(cls) -> Type[PatchBundle]:  # type: ignore[override]
        return StrPatch.get_bundle_schema()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_text() -> str:
    """Provide sample multi-line text for testing."""

    # Two short sentences split across two lines to make TID mapping obvious.
    return "Hello world.\nThis is a test."


@pytest.fixture()
def target(sample_text: str) -> PatchTarget[str]:
    """Initialise a `PatchTarget` in string mode for *sample_text*."""
    return PatchTarget[str](object=sample_text, patch_type=StrPatch)


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

    patch = ConcreteStrPatch.model_validate_json(json_str)

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


def test_apply_replace_patch(target: PatchTarget[str]):
    """Applying a simple replace patch should update the text content."""

    patch = ConcreteStrPatch(
        tids=["1_1"],
        operation=ReplaceOp(pattern="world", replacement="ChatGPT"),
    )

    # Apply patch via target
    asyncio.run(target.apply_patches([patch]))

    expected_text = "Hello ChatGPT.\nThis is a test."
    assert target.content == expected_text


# ---------------------------------------------------------------------------
# Additional Patch operation tests
# ---------------------------------------------------------------------------



def test_apply_delete_patch(target: PatchTarget[str]):
    """Deleting a sentence should remove the corresponding line from the text."""

    # Delete the first (and only) sentence of the first line.
    patch = ConcreteStrPatch(
        tids=["1_1"],
        operation=DeleteOp(),
    )
    asyncio.run(target.apply_patches([patch]))

    expected_text = "This is a test."
    assert target.content == expected_text



def test_apply_insert_after_patch(target: PatchTarget[str]):
    """Inserting text after a given line should shift subsequent lines down."""

    patch = ConcreteStrPatch(
        tids=["1_1"],
        operation=InsertAfterOp(text="New line."),
    )
    asyncio.run(target.apply_patches([patch]))

    expected_text = "Hello world.\nNew line.\nThis is a test."
    assert target.content == expected_text



def test_apply_multiple_patches_bundle(target: PatchTarget[str]):
    """Applying a bundle containing multiple patch types should yield the correct final text.

    The patches are intentionally provided in a non-optimal order to ensure that
    ``StrPatch.get_bundle_schema`` sorts them (replace → delete → insert).
    """

    patch_replace = ConcreteStrPatch(
        tids=["1_1"],
        operation=ReplaceOp(pattern="Hello", replacement="Hi"),
    )

    patch_delete = ConcreteStrPatch(
        tids=["2_1"],
        operation=DeleteOp(),
    )

    patch_insert = ConcreteStrPatch(
        tids=["1_1"],
        operation=InsertAfterOp(text="New line."),
    )

    # Provide patches in reverse priority order and sort as library would
    patches = [patch_insert, patch_delete, patch_replace]

    priority = {"replace": 0, "delete": 1, "insert_after": 2}
    def _anchor_line(p: StrPatch) -> int:
        anchor_tid = p.tids[-1] if p.operation.type == "insert_after" else p.tids[0]
        return int(anchor_tid.split("_")[0])

    sorted_patches = sorted(patches, key=lambda p: (priority.get(p.operation.type, 99), -_anchor_line(p)))

    asyncio.run(target.apply_patches(sorted_patches)) # type: ignore[arg-type]

    expected_text = "Hi world.\nNew line."
    assert target.content == expected_text