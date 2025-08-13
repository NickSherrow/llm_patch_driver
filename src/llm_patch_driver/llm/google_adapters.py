"""Google Gemini API adapter for models.generateContent via google-genai.

This adapter formats inputs and parses outputs to align with the
`BaseApiAdapter` interface so the driver can remain provider-agnostic.

It targets the Python client usage:

  from google import genai
  client = genai.Client()
  client.models.generate_content(model="gemini-2.0-flash", contents=...)

Key mappings (high-level):
- Messages -> `contents` (list of Content objects). Roles are mapped as:
  user -> user, assistant -> model. System prompts -> `system_instruction`.
- Tools -> `tools` with function declarations.
- Structured output -> `generation_config` with JSON mode when a schema is provided.

References: `models.generateContent` request/response shapes
`https://ai.google.dev/api/generate-content#method:-models.generatecontent`
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
import json

from pydantic import BaseModel
from glom import glom

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import (
    Message,
    ToolCallRequest,
    ToolCallResponse,
    ToolSchema,
)

U = TypeVar("U", bound=BaseModel)


class GoogleGenAiAdapter(BaseApiAdapter):
    """Adapter for Google Gemini models.generateContent.

    The formatted payload is designed for `google.genai.Client().models.generate_content`.
    """

    def format_llm_call_input(
        self,
        messages: List[Union[Message, ToolCallResponse]],
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[U]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format inputs for Gemini `models.generate_content`.

        Returns a dict of keyword arguments suitable for the google-genai client.
        """

        contents = []

        for msg in messages:

            match msg:

                case ToolCallResponse():
                    function_response_part = {
                        "functionResponse": {
                            "name": msg.request.name,
                            "response": {
                                "name": msg.request.name,
                                "content": [{"text": str(msg.output)}],
                            },
                        }
                    }
                    contents.append({
                        "role": "tool",
                        "parts": [function_response_part],
                    })
                    continue

                case Message():
                    # normalize role
                    if msg.role == "system":
                        msg.role = "user"

                    parts = []

                    # parse message content
                    if msg.content:
                        if isinstance(msg.content, str):
                            parts.append({"text": msg.content})
                        else:
                            parts.append(msg.content) # type: ignore

                    # parse tool calls
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            try:
                                args_obj = json.loads(tc.arguments)
                            except Exception:
                                args_obj = {"arguments": tc.arguments}
                            parts.append({
                                "functionCall": {
                                    "name": tc.name,
                                    "args": args_obj
                                }
                            })

                    contents.append({"role": msg.role, "parts": parts})

        model_params: Dict[str, Any] = {"contents": contents}

        # google-genai expects tools and schema inside GenerateContentConfig (config)
        config = {}

        if tools:
            config["tools"] = tools
            config["automatic_function_calling"] = {"disable": True}

        if system_prompt:
            config["system_instruction"] = system_prompt

        if schema:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = schema
            
        if config:
            model_params["config"] = config

        return model_params

    def format_tool_schema(self, tool_schema: ToolSchema) -> Dict[str, Any]:
        """Format a single tool into Gemini function declarations.

        Gemini expects `tools` to be a list where each entry can contain
        `functionDeclarations`. We package one function per schema here.
        """
        return {
            "functionDeclarations": [
                {
                    "name": tool_schema.name,
                    "description": tool_schema.description,
                    "parameters_json_schema": tool_schema.parameters,
                }
            ]
        }

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse Gemini response into a `Message` using client-surfaced fields.

        Only reads `text` and `function_calls` from the response, and preserves
        `parsed` if present for structured output.
        """

        content_text = glom(raw_response, "text", default="")
        structured_output = glom(raw_response, "parsed", default=None)
        fn_calls = glom(raw_response, "function_calls", default=[]) or []

        # Extract function calls directly from the response surface
        tool_calls: List[ToolCallRequest] = []
        
        for fc in fn_calls:
            name = glom(fc, "name", default="")
            args = glom(fc, "args", default={})

            if isinstance(args, (dict, list)):
                try:
                    arguments_str = json.dumps(args)
                except Exception:
                    arguments_str = str(args)
            else:
                arguments_str = str(args)

            tool_calls.append(
                ToolCallRequest(
                    type="function",
                    id="",
                    name=name,
                    arguments=arguments_str,
                )
            )

        return Message(
            role="model",
            content=content_text or "",
            tool_calls=tool_calls,
            attached_object=structured_output,
        )

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse provider-style messages into internal `Message` objects.

        Accepts a list of dicts with optional `role` and `parts`/`content` keys,
        or already-normalized `Message` objects.
        """

        parsed: List[Message] = []

        for msg in messages:
            if isinstance(msg, Message):
                parsed.append(msg)
                continue

            role = glom(msg, "role", default="user")
            if role == "system":
                role = "user"

            # Gemini Content does not have a top-level `content`; it has `parts`.
            parts = glom(msg, "parts", default=[])
            text_fragments: List[str] = []
            for part in parts:
                text_value = glom(part, "text", default=None)
                if isinstance(text_value, str):
                    text_fragments.append(text_value)

            parsed.append(Message(role=role, content="".join(text_fragments)))

        return parsed