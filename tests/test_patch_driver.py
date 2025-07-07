import pytest
import asyncio
from pydantic import BaseModel
from llm_patch_driver.driver.driver import PatchDriver
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.patch_schemas.string_patch import StrPatch, ReplaceOp, DeleteOp, InsertAfterOp
from llm_patch_driver.patch_schemas.json_patch import JsonPatch


def test_apply_string_patches():
    text = "Hello world.\nThis is a test."
    target = PatchTarget(object=text)
    driver = PatchDriver(target)

    bundle = driver.patch_schema.model_construct(
        patches=[StrPatch(tids=["1_1"], operation=ReplaceOp(pattern="Hello", replacement="Hi"))]
    )
    asyncio.run(driver.apply_patch_bundle(bundle))
    assert driver.patched_content.startswith("Hi")

    bundle = driver.patch_schema.model_construct(
        patches=[StrPatch(tids=["2_1"], operation=DeleteOp())]
    )
    asyncio.run(driver.apply_patch_bundle(bundle))
    assert "test" not in driver.patched_content

    bundle = driver.patch_schema.model_construct(
        patches=[StrPatch(tids=["1_1"], operation=InsertAfterOp(text="New line."))]
    )
    asyncio.run(driver.apply_patch_bundle(bundle))
    assert "New line." in driver.patched_content.splitlines()[1]


def test_apply_json_patches():
    class Schema(BaseModel):
        a: str
        b: list[int]

    obj = {"a": "x", "b": [1, 2]}
    target = PatchTarget(object=obj, validation_schema=Schema)
    driver = PatchDriver(target)

    driver._apply_patch(JsonPatch(op="replace", a_id=1, value="y"))
    assert obj["a"] == "y"

    driver._apply_patch(JsonPatch(op="add", a_id=2, i_id=3, value=3))
    assert obj["b"] == [1, 2, 3]

    driver._apply_patch(JsonPatch(op="remove", a_id=2, i_id=1, value=None))
    assert obj["b"] == [2, 3]
