from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Callable, List, Type, Optional, TypedDict, Tuple, TypeVar
from functools import partial, partialmethod
from glom import glom, SKIP, Iter, M, T

from llm_patch_driver.llm.api_schemas import RESPONSES_API_MAP, COMPLETION_API_MAP
from llm_patch_driver.llm.maps import ApiLLMMap, ToolCallRequestMap, ToolCallResponseMap, MessageMap
from llm_patch_driver.llm.types import ToolCallRequest, ToolCallResponse
from llm_patch_driver.config import config

U = TypeVar("U", bound=BaseModel)

class LLMClientWrapper:
    """Wrapper for LLM clients"""

    def __init__(self, 
                 llm_request_message: Callable, 
                 llm_request_object: Callable, 
                 model_args: dict, 
                 custom_map: Optional[ApiLLMMap] = None):
        
        self._create = partial(llm_request_message, **model_args)
        self._parse = partial(llm_request_object, **model_args)
        
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
        llm_response = await self._create(**model_params)

        # parse response with glom
        tool_calls = glom(llm_response, (self.api_map["output"]["tool_calls_path"], self._parse_tool_calls))
        output_message = glom(llm_response, (self.api_map["output"]["message_path"]))

        return tool_calls, output_message
    
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
        llm_response = await self._parse(**model_params)

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

        return [glom(tool_call, spec) for tool_call in tool_calls]
    
    def to_llm_message(self, content: str|dict|list, role: str) -> dict:
        """Normalize messages to the format expected by the LLM"""

        role_kw = self.api_map["message"]["role_kw"]
        content_kw = self.api_map["message"]["content_kw"]

        return {role_kw: role, content_kw: content}
    
    def format_tool_call_results(self, 
                                 tool_calls: List[Tuple[ToolCallRequest, ToolCallResponse]], 
                                 message: dict | None = None) -> list:
        """Format tool call results to the format expected by the LLM"""

        message_list = [] if message is None else [message]
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