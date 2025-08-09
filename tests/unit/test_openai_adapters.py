"""Unit tests for OpenAI adapters: `OpenAIChatCompletions` and `OpenAIResponses`."""

from llm_patch_driver.llm.openai_adapters import OpenAIChatCompletions, OpenAIResponses
from llm_patch_driver.llm.schemas import Message, ToolSchema


def test_chat_completions_format_and_parse_roundtrip():
    adapter = OpenAIChatCompletions()
    messages = [Message(role="user", content="hi")]
    payload = adapter.format_llm_call_input(messages=messages, tools=None, schema=None, system_prompt=None)  # type: ignore[arg-type]

    # Simulate an OpenAI response matching adapter expectations
    raw = {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
    parsed = adapter.parse_llm_output(raw)
    assert parsed.role == "assistant"
    assert parsed.content == "ok"

    # Tool schema formatting
    schema = ToolSchema(name="Echo", parameters={"type": "object"}, description="", strict=False, type="function")
    formatted = adapter.format_tool_schema(schema)
    assert formatted["function"]["name"] == "Echo"


def test_responses_format_and_parse_roundtrip():
    adapter = OpenAIResponses()
    messages = [Message(role="user", content="hi")]
    payload = adapter.format_llm_call_input(messages=messages, tools=None, schema=None, system_prompt="sys")  # type: ignore[arg-type]
    assert "instructions" in payload

    raw = {
        "output": [
            {"type": "message", "role": "assistant", "content": "ok"},
            {"type": "function_call", "call_id": "1", "name": "Echo", "arguments": "{}"},
        ],
        "output_parsed": None,
    }
    parsed = adapter.parse_llm_output(raw)
    assert parsed.role == "assistant"
    assert parsed.content == "ok"
    assert parsed.tool_calls and parsed.tool_calls[0].name == "Echo"

