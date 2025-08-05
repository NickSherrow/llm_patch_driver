"""OpenAI API adapters for Chat Completions and Responses APIs.

This module provides concrete implementations of BaseApiAdapter for OpenAI's
two main API formats:
1. Chat Completions API - Standard OpenAI chat format
2. Responses API - OpenAI's structured response format
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.types import ToolCallRequest, ToolCallResponse, Message

U = TypeVar("U", bound=BaseModel)


class OpenAIChatCompletions(BaseApiAdapter):
    """Adapter for OpenAI Chat Completions API.
    
    This adapter handles the standard OpenAI chat completion format used by
    GPT models for conversational interactions with optional tool calling.
    """

    def format_llm_call_input(
        self, 
        messages: List[Message], 
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[U]] = None,
        system_prompt: Optional[str] = None
        ) -> Dict[str, Any]:
        """Format inputs for OpenAI Chat Completions API."""
        
        model_params = {}
        
        # Handle system prompt by adding to messages list
        if system_prompt:
            model_params["messages"] = [{"role": "system", "content": system_prompt}]
        else:
            model_params["messages"] = []
            
        # Convert Message objects to OpenAI format and add to messages
        for msg in messages:
            msg_dict = {
                "role": msg.role,
                "content": msg.content
            }
            model_params["messages"].append(msg_dict)
        
        # Add tools if provided
        if tools:
            model_params["tools"] = tools
            
        # Add schema for structured output if provided
        if schema:
            model_params["response_format"] = schema
            
        return model_params

    def format_tool_results(
        self, 
        tool_calls: List[ToolCallResponse]
        ) -> List[dict]:
        """Format tool call results for OpenAI Chat Completions API.
        
        OpenAI Chat Completions API doesn't require the original request
        to be included (append=False), only the tool response.
        """
        
        message_list = []
        
        for tool_call in tool_calls:
            response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_call.output
            }
            message_list.append(response)
            
        return message_list

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse OpenAI Chat Completions response into Message."""
        
        # Extract message from choices[0].message
        message_data = raw_response["choices"][0]["message"]
        
        # Extract tool calls if present
        tool_calls = message_data.get("tool_calls", [])
        
        # Parse tool calls into ToolCallRequest format
        parsed_tool_calls = []
        if tool_calls:
            for tool_call in tool_calls:
                parsed_tool_calls.append(ToolCallRequest(
                    type=tool_call["type"],
                    id=tool_call["id"],
                    name=tool_call["function"]["name"],
                    arguments=tool_call["function"]["arguments"]
                ))
        
        # Check for structured output (parsed object)
        structured_output = raw_response.get("parsed")
        
        return Message(
            role=message_data.get("role", "assistant"),
            content=message_data.get("content", ""),
            tool_calls=parsed_tool_calls,
            attached_object=structured_output
        )

    def parse_object_from_llm_output(self, raw_response: Any) -> Any:
        """Parse structured object from OpenAI Chat Completions response."""
        
        # Extract structured output (parsed object)
        return raw_response.get("parsed")

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse OpenAI-formatted messages into Message objects."""
        
        parsed_messages = []
        
        for msg in messages:
            # Extract tool calls if present
            tool_calls = []
            if "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    tool_calls.append(ToolCallRequest(
                        type=tool_call.get("type", "function"),
                        id=tool_call.get("id", ""),
                        name=tool_call.get("function", {}).get("name", ""),
                        arguments=tool_call.get("function", {}).get("arguments", "")
                    ))
            
            # Check for structured output in the message
            structured_output = msg.get("parsed")
            
            parsed_messages.append(Message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                tool_calls=tool_calls,
                attached_object=structured_output
            ))
            
        return parsed_messages


class OpenAIResponses(BaseApiAdapter):
    """Adapter for OpenAI Responses API.
    
    This adapter handles OpenAI's newer Responses API format which provides
    a different structure for tool calling and message handling.
    """

    def format_llm_call_input(
        self, 
        messages: List[Message], 
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[U]] = None,
        system_prompt: Optional[str] = None
        ) -> Dict[str, Any]:
        """Format inputs for OpenAI Responses API."""
        
        model_params = {}
        
        # Handle system prompt differently for Responses API
        if system_prompt:
            model_params["instructions"] = system_prompt
            
        # Convert Message objects to Responses API format
        input_messages = []
        for msg in messages:
            input_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        model_params["input"] = input_messages
        
        # Add tools if provided
        if tools:
            model_params["tools"] = tools
            
        # Add schema for structured output if provided  
        if schema:
            model_params["text_format"] = schema
            
        return model_params

    def format_tool_results(
        self, 
        tool_calls: List[ToolCallResponse]
        ) -> List[dict]:
        """Format tool call results for OpenAI Responses API.
        
        OpenAI Responses API requires both the original request and response
        to be included (append=True).
        """
        
        message_list = []
        
        for tool_call in tool_calls:
            # First add the original request
            request = {
                "type": "function_call",
                "call_id": tool_call.id,
                "name": tool_call.request.name,
                "arguments": tool_call.request.arguments
            }
            message_list.append(request)
            
            # Then add the response
            response = {
                "type": "function_call_output",
                "call_id": tool_call.id,
                "output": tool_call.output
            }
            message_list.append(response)
            
        return message_list

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse OpenAI Responses API response into Message."""
        
        # Extract tool calls by filtering output array for function_call type
        output_items = raw_response.get("output", [])
        tool_calls_data = [item for item in output_items if item.get("type") == "function_call"]
        
        # Parse tool calls into ToolCallRequest format
        parsed_tool_calls = []
        for tool_call in tool_calls_data:
            parsed_tool_calls.append(ToolCallRequest(
                type=tool_call["type"],
                id=tool_call["call_id"],
                name=tool_call["name"],
                arguments=tool_call["arguments"]
            ))
        
        # Extract message by filtering for message type
        message_data = {}
        for item in output_items:
            if item.get("type") == "message":
                message_data = item
                break
        
        # Check for structured output (parsed object)
        structured_output = raw_response.get("output_parsed")
        
        return Message(
            role=message_data.get("role", "assistant"),
            content=message_data.get("content", ""),
            tool_calls=parsed_tool_calls,
            attached_object=structured_output
        )

    def parse_object_from_llm_output(self, raw_response: Any) -> Any:
        """Parse structured object from OpenAI Responses API response."""
        
        # Extract structured output (parsed object)
        return raw_response.get("output_parsed")

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse Responses API-formatted messages into Message objects."""
        
        parsed_messages = []
        
        for msg in messages:
            # Responses API has different tool call structure
            tool_calls = []
            if msg.get("type") == "function_call":
                tool_calls.append(ToolCallRequest(
                    type=msg.get("type", "function_call"),
                    id=msg.get("call_id", ""),
                    name=msg.get("name", ""),
                    arguments=msg.get("arguments", "")
                ))
            
            # Check for structured output in the message
            structured_output = msg.get("output_parsed")
            
            parsed_messages.append(Message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                tool_calls=tool_calls,
                attached_object=structured_output
            ))
            
        return parsed_messages