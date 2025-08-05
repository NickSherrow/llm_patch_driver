from openai import OpenAI
from dotenv import load_dotenv

from llm_patch_driver.llm.wrapper import LLMClientWrapper
from llm_patch_driver.driver.driver import PatchDriver
from llm_patch_driver import config

config.api_type = "chat_completion"

load_dotenv()

wrapper = LLMClientWrapper(
    llm_request_message=OpenAI().chat.completions.create,
    llm_request_object=OpenAI().chat.completions.create,
    model_args={},
    custom_map=None
)

def words_counter(text: str) -> int:
    return len(text.split())

from tests.integration.openai_e2e.test_string_assets import DOC

print(words_counter(DOC))