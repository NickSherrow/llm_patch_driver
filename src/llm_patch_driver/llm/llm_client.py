from __future__ import annotations

import logging
import inspect

from functools import partial, partialmethod
from typing import Any, Callable, List, Type, Optional, TypedDict, Tuple, TypeVar

from pydantic import BaseModel
from glom import glom, SKIP, Iter, M, T

from llm_patch_driver.llm.api_schemas import RESPONSES_API_MAP, COMPLETION_API_MAP
from llm_patch_driver.llm.maps import ApiLLMMap, ToolCallRequestMap, ToolCallResponseMap, MessageMap
from llm_patch_driver.llm.types import ToolCallRequest, ToolCallResponse
from llm_patch_driver.config import config
from llm_patch_driver.logging import log_wrapper, ArgSpec, OutputFormat

U = TypeVar("U", bound=BaseModel)

collector = config.build_log_collector(__name__)

class LLMClientWrapper:
    """Wrapper for LLM clients
    
    Args:
        llm_request_message: Function that requests a message from the LLM
        llm_request_object: Function that requests an object from the LLM
        model_args: Arguments to pass to the LLM
        custom_map: Custom map to use for the LLM
    """

    def __init__(self, 
                 llm_request_message: Callable, 
                 llm_request_object: Callable, 
                 model_args: dict, 
                 custom_map: Optional[ApiLLMMap] = None):
        
        self._create = (partial(llm_request_message, **model_args), inspect.iscoroutinefunction(llm_request_message))
        self._parse = (partial(llm_request_object, **model_args), inspect.iscoroutinefunction(llm_request_object))
        
        match config.api_type:
            case "responses":
                self.api_map = RESPONSES_API_MAP

            case "chat_completion":
                self.api_map = COMPLETION_API_MAP

            case "custom":
                if custom_map is None:
                    raise ValueError("custom_map is required when api_type is 'custom'")
                
                self.api_map = custom_map

            case _:
                raise ValueError(f"Invalid api_type: {config.api_type}")

    @log_wrapper(
        span_kind="llm",
        log_output=OutputFormat(rich_console=None, logger_level="INFO", otel_output=True),
        log_input=[
            ArgSpec("messages", None, None, "input", None),
            ArgSpec("tools", None, None, "metadata", None),
            ArgSpec("system_prompt", None, None, "metadata", None),
        ],
    )
    async def create_message(self,
                     messages: List[Any], 
                     tools: Optional[List[dict]] = None, 
                     system_prompt: Optional[str] = None
                     ) -> tuple[List[ToolCallRequest], Any]:
        
        """Create a message from the LLM"""

        # build inputs for llm call
        model_params = self.api_map["input"]["system_prompt_dict"](system_prompt) if system_prompt else {}
        model_params.setdefault(self.api_map["input"]["messages_kw"], []).extend(messages) 
        model_params.setdefault(self.api_map["input"]["tools_kw"], []).extend(tools)
        # get response

        match self._create:
            case (func, True):
                llm_response = await func(**model_params)
            case (func, False):
                llm_response = func(**model_params)
            case _:
                raise ValueError("Invalid function type")

        # parse response with glom
        tool_calls = glom(llm_response, (self.api_map["output"]["tool_calls_path"], self._parse_tool_calls))
        output_message = glom(llm_response, (self.api_map["output"]["message_path"]))

        return tool_calls, output_message
    
    @log_wrapper(
        log_output=OutputFormat(rich_console=None, logger_level="INFO", otel_output=True),
        log_input=[
            ArgSpec("messages", None, None, "input", None),
            ArgSpec("schema", None, None, "metadata", None),
            ArgSpec("system_prompt", None, None, "metadata", None),
        ],
        span_kind="llm"
    )
    async def create_object(self, 
                    messages: List[Any], 
                    schema: Type[U], 
                    system_prompt: Optional[str] = None
                    ) -> U:
        
        """Create an object with the LLM"""

        # build inputs for llm call
        model_params = self.api_map["input"]["system_prompt_dict"](system_prompt) if system_prompt else {}
        model_params.setdefault(self.api_map["input"]["messages_kw"], []).extend(messages) 
        model_params[self.api_map["input"]["schema_kw"]] = schema

        # parse response
        match self._parse:
            case (func, True):
                llm_response = await func(**model_params)
            case (func, False):
                llm_response = func(**model_params)
            case _:
                raise ValueError("Invalid function type")

        # parse response with glom
        parsed_object = glom(llm_response, self.api_map["output"]["parsed_object_path"])

        return parsed_object
    
    def _parse_tool_calls(self, tool_calls: List[dict]) -> List[ToolCallRequest]:
        """Normalize tool calls to the format expected by the LLM"""

        if not tool_calls:
            return []

        spec = {
            "type": self.api_map["tool_call_request"]["type_path"],
            "id": self.api_map["tool_call_request"]["id_path"],
            "name": self.api_map["tool_call_request"]["name_path"],
            "arguments": self.api_map["tool_call_request"]["arguments_path"]
        }

        return [ToolCallRequest(**glom(tool_call, spec)) for tool_call in tool_calls]
    
    def to_llm_message(self, content: str|dict|list, role: str) -> dict:
        """Normalize messages to the format expected by the LLM"""

        role_kw = self.api_map["message"]["role_kw"]
        content_kw = self.api_map["message"]["content_kw"]

        return {role_kw: role, content_kw: content}
    
    def format_tool_call_results(self, 
                                 tool_calls: List[Tuple[ToolCallRequest, ToolCallResponse]]
                                 ) -> list:
        """Format tool call results to the format expected by the LLM"""

        message_list = []
        append_request = self.api_map["tool_call_request"]["append"]

        for tool_call in tool_calls:
            if append_request:
                request = {
                    self.api_map["tool_call_request"]["type_path"]: self.api_map["tool_call_request"]["type_value"],
                    self.api_map["tool_call_request"]["id_path"]: tool_call[0].id,
                    self.api_map["tool_call_request"]["name_path"]: tool_call[0].name,
                    self.api_map["tool_call_request"]["arguments_path"]: tool_call[0].arguments
                }
                message_list.append(request)
            response = {
                self.api_map["tool_call_response"]["type_kw"]: self.api_map["tool_call_response"]["type_value"],
                self.api_map["tool_call_response"]["id_kw"]: tool_call[0].id,
                self.api_map["tool_call_response"]["output_kw"]: tool_call[1].output
                }
            message_list.append(response)

        return message_list