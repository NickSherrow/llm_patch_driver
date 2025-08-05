import pytest
import asyncio
from pydantic import BaseModel, ValidationError

from llm_patch_driver.patch_target.target import PatchTarget


class PersonModel(BaseModel):
    name: str


# --------------------------------------------------------------------- #
# INITIALIZATION TESTS
# --------------------------------------------------------------------- #

def test_patch_target_initialization_with_string():
    """PatchTarget can wrap a plain string without extra arguments."""
    pt = PatchTarget(object="hello world")
    assert pt.content == "hello world"
    assert pt.content_attribute is None


def test_patch_target_initialization_with_attribute():
    """PatchTarget correctly uses the provided content_attribute if it exists on the object."""

    class Dummy:
        def __init__(self) -> None:
            self.text = "dummy"

    dummy = Dummy()
    pt = PatchTarget(object=dummy, content_attribute="text")
    assert pt.content == "dummy"


# --------------------------------------------------------------------- #
# VALIDATION – ERROR CONDITIONS AT INITIALISATION
# --------------------------------------------------------------------- #

def test_patch_target_initialization_invalid_attribute():
    """Initialization fails if content_attribute is missing on the object."""

    class Dummy:  # does not have `missing` attribute
        pass

    with pytest.raises(ValueError):
        PatchTarget(object=Dummy(), content_attribute="missing")


def test_patch_target_initialization_non_string_without_schema():
    """Initialization fails for non-string object when no validation schema is supplied."""
    with pytest.raises(ValueError):
        PatchTarget(object=123)  # type: ignore[arg-type]


# --------------------------------------------------------------------- #
# VALIDATE_CONTENT – SCHEMA-BASED VALIDATION
# --------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_validate_content_with_schema_success():
    pt = PatchTarget(object={"name": "Alice"}, validation_schema=PersonModel)
    result = await pt.validate_content()
    assert result is None


@pytest.mark.asyncio
async def test_validate_content_with_schema_failure():
    pt = PatchTarget(object={}, validation_schema=PersonModel)
    result = await pt.validate_content()
    # The returned string should include the missing field name
    assert isinstance(result, str) and "name" in result


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
    pt = PatchTarget(object="invalid", validation_condition=sync_condition)
    result = await pt.validate_content()
    assert result == "sync error"


@pytest.mark.asyncio
async def test_validate_content_with_async_condition():
    pt = PatchTarget(object="invalid", validation_condition=async_condition)
    result = await pt.validate_content()
    assert result == "async error"