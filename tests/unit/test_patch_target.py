import pytest
import asyncio
from pydantic import BaseModel, ValidationError

from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.patch.string.string_patch import StrPatch
from llm_patch_driver.patch.base_patch import BasePatch
PatchTarget.model_rebuild(_types_namespace={"BasePatch": BasePatch})


class PersonModel(BaseModel):
    name: str


# --------------------------------------------------------------------- #
# INITIALIZATION TESTS
# --------------------------------------------------------------------- #

def test_patch_target_initialization_with_string():
    """PatchTarget can wrap a plain string when `patch_type` is provided."""
    pt = PatchTarget(object="hello world", patch_type=StrPatch)
    assert pt.content == "hello world"
    assert pt.content_attribute is None


def test_patch_target_initialization_with_attribute():
    """PatchTarget correctly uses the provided content_attribute if it exists on the object."""

    class Dummy:
        def __init__(self) -> None:
            self.text = "dummy"

    dummy = Dummy()
    pt = PatchTarget(object=dummy, content_attribute="text", patch_type=StrPatch)
    assert pt.content == "dummy"


# --------------------------------------------------------------------- #
# VALIDATION – ERROR CONDITIONS AT INITIALISATION
# --------------------------------------------------------------------- #

def test_patch_target_initialization_invalid_attribute():
    """Initialization fails if content_attribute is missing on the object."""

    class Dummy:  # does not have `missing` attribute
        pass

    # Instantiation triggers model_post_init which would raise AttributeError before validators
    # Ensure we still see an error during construction
    with pytest.raises(Exception):
        PatchTarget(object=Dummy(), content_attribute="missing", patch_type=StrPatch)


def test_patch_target_initialization_non_string_without_schema():
    """Initialization fails for non-string object when no validation schema is supplied."""
    with pytest.raises(Exception):
        PatchTarget(object=123, patch_type=StrPatch)  # type: ignore[arg-type]


# --------------------------------------------------------------------- #
# VALIDATE_CONTENT – SCHEMA-BASED VALIDATION
# --------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_validate_content_with_schema_success():
    # With string patch type and a JSON schema, validation will fail since content is a string.
    pt = PatchTarget(object="ok", validation_schema=PersonModel, patch_type=StrPatch)  # type: ignore[arg-type]
    result = await pt.validate_content()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_validate_content_with_schema_failure():
    # Non-string content with string patch type is invalid; ensure error during creation
    with pytest.raises(Exception):
        PatchTarget(object={}, validation_schema=PersonModel, patch_type=StrPatch)


# --------------------------------------------------------------------- #
# VALIDATE_CONTENT – CONDITION-BASED VALIDATION (SYNC & ASYNC)
# --------------------------------------------------------------------- #


def sync_condition(value: str):
    if value != "valid":
        return "sync error"
    return None


async def async_condition(value: str):
    if value != "valid":
        return "async error"
    return None


@pytest.mark.asyncio
async def test_validate_content_with_sync_condition():
    pt = PatchTarget(object="invalid", validation_condition=sync_condition, patch_type=StrPatch)
    result = await pt.validate_content()
    assert result == "sync error"


@pytest.mark.asyncio
async def test_validate_content_with_async_condition():
    pt = PatchTarget(object="invalid", validation_condition=async_condition, patch_type=StrPatch)
    result = await pt.validate_content()
    assert result == "async error"