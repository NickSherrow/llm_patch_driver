import asyncio

from openai import OpenAI
from rich.logging import RichHandler
from dotenv import load_dotenv
from phoenix.otel import register

from llm_patch_driver import PatchDriver
from llm_patch_driver.llm.google_adapters import GoogleGenAiAdapter
from .test_json_assets import json_target, messages

from google.auth import default
import os
from google import genai

load_dotenv()

location = os.getenv("GCP_LOCATION")
project_id = os.getenv("GCP_PROJECT_ID")

client = genai.Client(
    vertexai=True, project=project_id, location=location
)

phoenix_provider = register(
    project_name="llm-patch-driver",
    endpoint="https://phoenix-605569343938.us-west1.run.app/v1/traces",
    batch=True,
    auto_instrument=True
)

tracer = phoenix_provider.get_tracer(__name__)

load_dotenv()

async def json_test():
    error = await json_target.validate_content()

    if error:
        json_target.current_error = error  # needed so the loop starts
        create_method = client.models.generate_content
        parse_method = client.models.generate_content
        driver = PatchDriver(json_target, create_method, parse_method, {'model': 'google/gemini-2.5-pro'}, GoogleGenAiAdapter())
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(json_target.content)
        print("===== PATCHED STATE =====")
        print(json_target.content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(json_test())