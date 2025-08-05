import asyncio
import logging

from openai import OpenAI
from rich.logging import RichHandler
from dotenv import load_dotenv
from phoenix.otel import register

from llm_patch_driver import config, PatchDriver, LLMClientWrapper
from .test_json_assets import json_target, messages

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler(rich_tracebacks=True)])
logging.getLogger("openai").setLevel(logging.WARNING)

phoenix_provider = register(
    project_name="llm-patch-driver",
    endpoint="https://phoenix-605569343938.us-west1.run.app/v1/traces",
    batch=True,
    auto_instrument=True
)

config.api_type = "chat_completion"
config.otel_provider = phoenix_provider # type: ignore

load_dotenv()

wrapper = LLMClientWrapper(
    llm_request_message=OpenAI().chat.completions.create,
    llm_request_object=OpenAI().chat.completions.create,
    model_args={'model': 'gpt-4.1'},
    custom_map=None
)

async def json_test():
    error = await json_target.validate_content()

    PatchDriver.client = wrapper

    if error:
        driver = PatchDriver(json_target, error)
        await driver.run_patching_loop(messages)
        print("===== ORIGINAL STATE =====")
        print(driver.original_content)
        print("===== PATCHED STATE =====")
        print(driver.patched_content)
        print("=========================")

if __name__ == "__main__":
    asyncio.run(json_test())