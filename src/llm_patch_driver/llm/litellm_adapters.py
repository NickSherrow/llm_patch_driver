"""LiteLLM adapter targeting the OpenAI-compatible Chat Completions surface.

LiteLLM exposes a unified OpenAI-style interface across many providers.
This adapter mirrors the OpenAI Chat Completions mapping so the driver can
call any LiteLLM-routed model via the same standardized interface.

References:
- Input shape (OpenAI-compatible): https://docs.litellm.ai/docs/completion/input
- Output shape (OpenAI-compatible): https://docs.litellm.ai/docs/completion/output
- Usage notes: https://docs.litellm.ai/docs/completion/usage
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel
from glom import glom

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import ToolCallRequest, ToolCallResponse, Message, ToolSchema

U = TypeVar("U", bound=BaseModel)


class LiteLLMChatCompletions(BaseApiAdapter):
    """Adapter for LiteLLM OpenAI-style Chat Completions API.

    This mirrors `OpenAIChatCompletions` since LiteLLM returns the same
    response format and accepts the same input parameters for chat.
    """

    def format_llm_call_input(
        self,
        messages: List[Message | ToolCallResponse],
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[U]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format inputs for LiteLLM Chat Completions (OpenAI format).

        Returns kwargs ready to pass to a `client.chat.completions.create`-style method.
        """

        model_params: Dict[str, Any] = {}

        # System prompt becomes a leading system message
        if system_prompt:
            model_params["messages"] = [{"role": "system", "content": system_prompt}]
        else:
            model_params["messages"] = []

        # Convert standardized Message/ToolCallResponse into OpenAI-format messages
        for msg in messages:
            match msg:
                case Message():
                    msg_dict: Dict[str, Any] = {"role": msg.role}
                    if msg.content is not None:
                        msg_dict["content"] = msg.content

                    if msg.tool_calls:
                        formatted_tool_calls = []
                        for tool_call in msg.tool_calls:
                            formatted_tool_calls.append(
                                {
                                    "id": tool_call.id,
                                    "type": tool_call.type,
                                    "function": {
                                        "name": tool_call.name,
                                        "arguments": tool_call.arguments,
                                    },
                                }
                            )
                        msg_dict["tool_calls"] = formatted_tool_calls

                case ToolCallResponse():
                    msg_dict = {
                        "role": "tool",
                        "tool_call_id": msg.id,
                        "content": msg.output,
                    }

            model_params["messages"].append(msg_dict)

        if tools:
            model_params["tools"] = tools

        # For structured output, LiteLLM supports OpenAI v2-style response_format models
        # that accept a pydantic schema / json schema via `response_format`.
        if schema:
            model_params["response_format"] = schema

        return model_params

    def format_tool_schema(self, tool_schema: ToolSchema) -> Dict[str, Any]:
        """Format tool schema to OpenAI function-calling shape."""
        return {
            "type": "function",
            "function": {
                "name": tool_schema.name,
                "parameters": tool_schema.parameters,
                "description": tool_schema.description,
                "strict": tool_schema.strict,
            },
        }

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse LiteLLM Chat Completions response into a Message.

        The response mirrors OpenAI's shape:
        choices[0].message{ role, content, tool_calls? }, plus `parsed` for structured output.
        """

        message_data = glom(raw_response, "choices.0.message", default={})

        tool_calls_raw = glom(message_data, "tool_calls", default=[]) or []
        parsed_tool_calls: List[ToolCallRequest] = []
        for tc in tool_calls_raw:
            parsed_tool_calls.append(
                ToolCallRequest(
                    type=glom(tc, "type", default="function"),
                    id=glom(tc, "id", default=""),
                    name=glom(tc, "function.name", default=""),
                    arguments=glom(tc, "function.arguments", default=""),
                )
            )

        structured_output = glom(raw_response, "parsed", default=None)

        return Message(
            role=glom(message_data, "role", default="assistant"),
            content=glom(message_data, "content", default=""),
            tool_calls=parsed_tool_calls,
            attached_object=structured_output,
        )

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse OpenAI-format messages into internal Message objects."""

        parsed_messages: List[Message] = []
        for msg in messages:
            tool_calls_list: List[ToolCallRequest] = []
            for tc in glom(msg, "tool_calls", default=[]) or []:
                tool_calls_list.append(
                    ToolCallRequest(
                        type=glom(tc, "type", default="function"),
                        id=glom(tc, "id", default=""),
                        name=glom(tc, "function.name", default=""),
                        arguments=glom(tc, "function.arguments", default=""),
                    )
                )

            structured_output = glom(msg, "parsed", default=None)

            parsed_messages.append(
                Message(
                    role=glom(msg, "role", default="user"),
                    content=glom(msg, "content", default=""),
                    tool_calls=tool_calls_list,
                    attached_object=structured_output,
                )
            )

        return parsed_messages


