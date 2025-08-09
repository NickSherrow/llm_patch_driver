"""Unit tests for `PatchDriver` public API shape with a fake adapter.

We validate:
- Formatting inputs via the adapter
- Parsing outputs via the adapter
- Tool binding prepares tool schemas using adapter
"""

import asyncio
from typing import Any, Dict, List, Optional, Type

import pytest
from pydantic import BaseModel

from llm_patch_driver.driver.driver import PatchDriver
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.patch.string.string_patch import StrPatch
from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import Message, ToolCallRequest
from llm_patch_driver.llm.base_tool import LLMTool
from llm_patch_driver.patch.base_patch import BasePatch

PatchTarget.model_rebuild(_types_namespace={"BasePatch": BasePatch})

class DummyAdapter(BaseApiAdapter):
    def format_llm_call_input(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[BaseModel]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Echo inputs for inspection
        return {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "tools": tools or [],
            "schema": schema,
            "system_prompt": system_prompt,
        }

    def format_tool_schema(self, tool_schema):
        return {"name": tool_schema.name, "parameters": tool_schema.parameters}

    def parse_llm_output(self, raw_response: Any) -> Message:
        # Produce a simple assistant message
        return Message(role="assistant", content="ok")

    def parse_messages(self, messages: list) -> List[Message]:  # type: ignore[override]
        return [Message(role=m.get("role", "user"), content=m.get("content", "")) for m in messages]


async def _fake_create(**kwargs):
    return {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}


def _fake_parse(**kwargs):
    return {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}


def test_call_llm_uses_adapter_format_and_parse():
    target = PatchTarget(object="hello world", patch_type=StrPatch)
    driver = PatchDriver(
        target_object=target,
        create_method=_fake_create,
        parse_method=_fake_parse,
        api_adapter=DummyAdapter(),
        tools=[],
    )

    msg = asyncio.run(driver.call_llm(messages=[Message(role="user", content="hello")]))
    assert isinstance(msg, Message)
    assert msg.role == "assistant"


def test_bind_tool_registers_schema():
    target = PatchTarget(object="hello world", patch_type=StrPatch)
    driver = PatchDriver(
        target_object=target,
        create_method=_fake_create,
        parse_method=_fake_parse,
        api_adapter=DummyAdapter(),
        tools=[],
    )

    class EchoTool(LLMTool):
        text: str

        async def __call__(self) -> str:  # type: ignore[override]
            return self.text

    driver.bind_tool(EchoTool)
    # The internal _tools should have one formatted schema entry
    assert any(s.get("name") == "EchoTool" for s in driver._tools)  # type: ignore[attr-defined]
