import pytest
import asyncio
from pydantic import BaseModel
from llm_patch_driver.patch_target.target import PatchTarget


class Schema(BaseModel):
    text: str


def test_validate_content_schema_error():
    target = PatchTarget(object={"text": 123}, validation_schema=Schema)
    err = asyncio.run(target.validate_content())
    assert "validation error" in err


def test_invalid_attribute():
    class Dummy:
        pass
    with pytest.raises(ValueError):
        PatchTarget(object=Dummy(), content_attribute="missing")


def test_missing_schema_for_non_string():
    with pytest.raises(ValueError):
        PatchTarget(object={}, validation_schema=None)
