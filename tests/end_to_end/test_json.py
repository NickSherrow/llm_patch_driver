"""
> JSON patching loop test case

This test simulates the following scenario:
- LLM is given a call transcript and a JSON with supportive structured data.
- LLM is asked to extract the company hierarchy from the transcript and the JSON.
- The expected output is a nested recursive JSON with the company hierarchy.
- Extracted object must pass Pydantic validation that is defined in the Company class.

We provide a corrupted version of the extracted object that has multiple validation errors
to the PatchDriver with previous conversation history and validation schema. We expect
the PatchDriver to fix all the violations and return a valid JSON.
"""

import asyncio
import os

from dotenv import load_dotenv
from phoenix.otel import register
from google import genai

from llm_patch_driver import PatchDriver
from llm_patch_driver.llm.google_adapters import GoogleGenAiAdapter
from .test_json_assets import json_target, messages, Company

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

tracer = phoenix_provider.get_tracer(__name__)

async def json_test():
    error = await json_target.validate_content()

    if error:
        json_target.current_error = error  # needed so the loop starts
        create_method = client.models.generate_content
        parse_method = client.models.generate_content
        driver = PatchDriver(
            json_target, 
            create_method, 
            parse_method, 
            {'model': 'gemini-2.5-pro'}, 
            GoogleGenAiAdapter()
            )
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(json_target.content)
        print("===== PATCHED STATE =====")
        print(json_target.content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(json_test())