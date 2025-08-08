import asyncio
import logging

from openai import OpenAI
from rich.logging import RichHandler
from dotenv import load_dotenv
from phoenix.otel import register

from llm_patch_driver import config, PatchDriver
from .test_json_assets import json_target, messages

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler(rich_tracebacks=True, markup=True,)])
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
        create_method = OpenAI().chat.completions.create
        model_args = {'model': 'gpt-4.1'}
        parse_method = OpenAI().chat.completions.parse
        driver = PatchDriver(json_target, create_method, parse_method, model_args)
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(json_target.content)
        print("===== PATCHED STATE =====")
        print(json_target.content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(json_test())