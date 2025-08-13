"""
> String patching loop test case

This test simulates the following scenario:
- LLM is given a prompt to generate an employee agreement that follows a set of rules.
- The rules are defined in the validation_string_condition function. They include both
deterministc conditions (word count) and probabalistic conditions (presence of specific
terms and sections).

We provide a corrupted version of the agreement that violates the rules. We expect
the PatchDriver to fix all the violations and return a valid agreement that follows
the rules.
"""

import asyncio
import os

from functools import partial

from dotenv import load_dotenv
from phoenix.otel import register
from google import genai

from llm_patch_driver import PatchDriver, PatchTarget, StrPatch
from llm_patch_driver.llm.google_adapters import GoogleGenAiAdapter
from .test_string_assets import messages, validation_string_condition, DOC

load_dotenv()

location = os.getenv("GCP_LOCATION")
project_id = os.getenv("GCP_PROJECT_ID")
endpoint = os.getenv("OTEL_ENDPOINT")

client = genai.Client(
    vertexai=True, project=project_id, location=location
)

phoenix_provider = register(
    project_name="llm-patch-driver",
    endpoint=endpoint,
    batch=True,
    auto_instrument=True
)

target_object = PatchTarget(
    object=DOC,
    validation_condition=partial(validation_string_condition, call_llm=client.models.generate_content),
    patch_type=StrPatch
)

tracer = phoenix_provider.get_tracer(__name__)

async def string_test():
    error = await target_object.validate_content()

    if error:
        target_object.current_error = error  # needed so the loop starts
        create_method = client.models.generate_content
        parse_method = client.models.generate_content
        driver = PatchDriver(
            target_object, 
            create_method, 
            parse_method, 
            {'model': 'gemini-2.5-pro'}, 
            GoogleGenAiAdapter()
            )
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(target_object.content)
        print("===== PATCHED STATE =====")
        print(target_object.content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(string_test())