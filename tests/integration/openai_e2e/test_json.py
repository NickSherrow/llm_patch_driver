import asyncio
import logging

from openai import OpenAI
from rich.logging import RichHandler
from dotenv import load_dotenv
from phoenix.otel import register

from llm_patch_driver import config, PatchDriver
from .test_json_assets import json_target, messages

logging.basicConfig(level=logging.INFO, handlers=[RichHandler(rich_tracebacks=True, markup=True,)])
logging.getLogger("openai").setLevel(logging.WARNING)

phoenix_provider = register(
    project_name="llm-patch-driver",
    endpoint="https://phoenix-605569343938.us-west1.run.app/v1/traces",
    batch=True,
    auto_instrument=True
)

config.otel_provider = phoenix_provider # type: ignore

load_dotenv()

async def json_test():
    error = await json_target.validate_content()

    if error:
        json_target.current_error = error  # needed so the loop starts
        create_method = OpenAI().chat.completions.create
        parse_method = OpenAI().chat.completions.parse
        driver = PatchDriver(json_target, create_method, parse_method, {'model': 'gpt-5-mini'})
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(json_target.content)
        print("===== PATCHED STATE =====")
        print(json_target.content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(json_test())