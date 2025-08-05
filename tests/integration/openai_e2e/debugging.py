import asyncio

from llm_patch_driver.patch_target.target import PatchTarget
from .test_json_assets import Company, TEST_JSON, TestingJsonPatch

test_object = TestingJsonPatch(raw_json=TEST_JSON, some_attribute="test")

test_target = PatchTarget(object=test_object, content_attribute="raw_json", validation_schema=Company)

print(asyncio.run(test_target.validate_content()))
#print(test_target.content)