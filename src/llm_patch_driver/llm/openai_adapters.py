"""OpenAI API adapters for Chat Completions and Responses APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel
from glom import glom

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import ToolCallRequest, ToolCallResponse, Message, ToolSchema

U = TypeVar("U", bound=BaseModel)

class OpenAIChatCompletions(BaseApiAdapter):
    """Adapter for OpenAI Chat Completions API."""

    def format_llm_call_input(
        self, 
        messages: List[Message | ToolCallResponse], 
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
            match msg:
                case Message():
                    msg_dict: Dict[str, Any] = {"role": msg.role}

                    # Attach content only if not None
                    if msg.content is not None:
                        msg_dict["content"] = msg.content

                    # Attach tool_calls if present on the message
                    if msg.tool_calls:
                        formatted_tool_calls = []
                        for tool_call in msg.tool_calls:
                            tc = {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": tool_call.arguments,
                                },
                            }
                            formatted_tool_calls.append(tc)
                        msg_dict["tool_calls"] = formatted_tool_calls

                case ToolCallResponse():
                    msg_dict = {
                        "role": "tool",
                        "tool_call_id": msg.id,
                        "content": msg.output
                    }
            model_params["messages"].append(msg_dict)
        
        # Add tools if provided
        if tools:
            model_params["tools"] = tools
            
        # Add schema for structured output if provided
        if schema:
            model_params["response_format"] = schema
            
        return model_params
    
    def format_tool_schema(self, tool_schema: ToolSchema) -> Dict[str, Any]:
        """Format a tool call into a dictionary of parameters ready to pass to the LLM API."""
        return {
            "type": "function",
            "function": {
                "name": tool_schema.name,
                "parameters": tool_schema.parameters,
                "description": tool_schema.description,
                "strict": tool_schema.strict
            }
        }

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse OpenAI Chat Completions response into Message."""
        
        # Extract message from choices.0.message (robust to dicts or objects)
        message_data = glom(raw_response, "choices.0.message", default={})
        
        # Extract tool calls if present
        tool_calls = glom(message_data, "tool_calls", default=[])
        
        # Parse tool calls into ToolCallRequest format
        parsed_tool_calls = []
        if tool_calls:
            for tool_call in tool_calls:
                parsed_tool_calls.append(
                    ToolCallRequest(
                        type=glom(tool_call, "type", default="function"),
                        id=glom(tool_call, "id", default=""),
                        name=glom(tool_call, "function.name", default=""),
                        arguments=glom(tool_call, "function.arguments", default=""),
                    )
                )
        
        # Check for structured output (parsed object)
        structured_output = glom(raw_response, "parsed", default=None)
        
        return Message(
            role=glom(message_data, "role", default="assistant"),
            content=glom(message_data, "content", default=""),
            tool_calls=parsed_tool_calls,
            attached_object=structured_output
        )

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse OpenAI-formatted messages into Message objects."""
        
        parsed_messages = []
        
        for msg in messages:
            # Extract tool calls if present
            tool_calls = []
            msg_tool_calls = glom(msg, "tool_calls", default=[])
            if msg_tool_calls:
                for tool_call in msg_tool_calls:
                    tool_calls.append(
                        ToolCallRequest(
                            type=glom(tool_call, "type", default="function"),
                            id=glom(tool_call, "id", default=""),
                            name=glom(tool_call, "function.name", default=""),
                            arguments=glom(tool_call, "function.arguments", default=""),
                        )
                    )
            
            # Check for structured output in the message
            structured_output = glom(msg, "parsed", default=None)
            
            parsed_messages.append(Message(
                role=glom(msg, "role", default="user"),
                content=glom(msg, "content", default=""),
                tool_calls=tool_calls,
                attached_object=structured_output
            ))
            
        return parsed_messages


class OpenAIResponses(BaseApiAdapter):
    """Adapter for OpenAI Responses API"""

    def format_llm_call_input(
        self, 
        messages: List[Message | ToolCallResponse], 
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

            match msg:
                case Message():
                    input_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                case ToolCallResponse():
                    input_messages.append({
                        "type": "function_call",
                        "call_id": msg.id,
                        "name": msg.request.name,
                        "arguments": msg.request.arguments
                    })
                    input_messages.append({
                        "type": "function_call_output",
                        "call_id": msg.id,
                        "output": msg.output
                    })

        
        model_params["input"] = input_messages
        
        # Add tools if provided
        if tools:
            model_params["tools"] = tools
            
        # Add schema for structured output if provided  
        if schema:
            model_params["text_format"] = schema
            
        return model_params
    
    def format_tool_schema(self, tool_schema: ToolSchema) -> Dict[str, Any]:
        """Format a tool call into a dictionary of parameters ready to pass to the OpenAI ResponsesAPI."""
        return {
            "type": "function",
            "name": tool_schema.name,
            "parameters": tool_schema.parameters,
            "description": tool_schema.description
        }

    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse OpenAI Responses API response into Message."""
        
        # Extract tool calls by filtering output array for function_call type
        output_items = glom(raw_response, "output", default=[])
        tool_calls_data = [item for item in output_items if glom(item, "type", default=None) == "function_call"]
        
        # Parse tool calls into ToolCallRequest format
        parsed_tool_calls = []
        for tool_call in tool_calls_data:
            parsed_tool_calls.append(
                ToolCallRequest(
                    type=glom(tool_call, "type", default="function_call"),
                    id=glom(tool_call, "call_id", default=""),
                    name=glom(tool_call, "name", default=""),
                    arguments=glom(tool_call, "arguments", default=""),
                )
            )
        
        # Extract message by filtering for message type
        message_data = {}
        for item in output_items:
            if glom(item, "type", default=None) == "message":
                message_data = item
                break
        
        # Check for structured output (parsed object)
        structured_output = glom(raw_response, "output_parsed", default=None)
        
        return Message(
            role=glom(message_data, "role", default="assistant"),
            content=glom(message_data, "content", default=""),
            tool_calls=parsed_tool_calls,
            attached_object=structured_output
        )

    def parse_messages(self, messages: list) -> List[Message]:
        """Parse Responses API-formatted messages into Message objects."""
        
        parsed_messages = []
        
        for msg in messages:
            # Responses API has different tool call structure
            tool_calls = []
            if glom(msg, "type", default=None) == "function_call":
                tool_calls.append(
                    ToolCallRequest(
                        type=glom(msg, "type", default="function_call"),
                        id=glom(msg, "call_id", default=""),
                        name=glom(msg, "name", default=""),
                        arguments=glom(msg, "arguments", default=""),
                    )
                )
            
            # Check for structured output in the message
            structured_output = glom(msg, "output_parsed", default=None)
            
            parsed_messages.append(Message(
                role=glom(msg, "role", default="user"),
                content=glom(msg, "content", default=""),
                tool_calls=tool_calls,
                attached_object=structured_output
            ))
            
        return parsed_messages