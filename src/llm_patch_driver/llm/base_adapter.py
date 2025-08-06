"""
LLM API adapter interface. Goal: to keep the library agnostic 
to the LLM provider with least amount of code.
"""

from __future__ import annotations

import inspect
from functools import partial

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Callable

from pydantic import BaseModel

from llm_patch_driver.llm.schemas import ToolCallRequest, ToolCallResponse, Message, ToolSchema

U = TypeVar("U", bound=BaseModel)


class BaseApiAdapter(ABC):
    """Abstract base class for LLM API adapters.
    
    Each concrete adapter implements provider-specific logic for:
    1. Converting standardized inputs into provider-specific API calls
    2. Parsing provider responses into standardized internal types
    3. Formatting messages and tool interactions according to provider schemas
    
    This abstraction allows the PatchDriver to work with any LLM provider
    without knowing the specifics of each provider's API format.
    """

    @abstractmethod
    def format_llm_call_input(
        self, 
        messages: List[Message], 
        tools: Optional[List[dict]] = None,
        schema: Optional[Type[U]] = None,
        system_prompt: Optional[str] = None
        ) -> Dict[str, Any]:
        """Format LLM inputs for an API call.
        
        Args:
            messages: List of messages
            tools: Optional list of available tools/functions
            schema: Optional Pydantic/JSON defining the expected response structure
            system_prompt: Optional system prompt to include
            
        Returns:
            Dictionary of parameters ready to pass to the LLM API
        """
        pass

    @abstractmethod
    def format_tool_schema(self, tool_schema: ToolSchema) -> Dict[str, Any]:
        """Format a tool call into a dictionary of parameters ready to pass to the LLM API."""
        pass

    # Handlers to parse outputs from the LLM API

    @abstractmethod
    def parse_llm_output(self, raw_response: Any) -> Message:
        """Parse a response from the LLM API into a message and tool calls.
        
        Args:
            raw_response: Raw response object from the LLM API
            
        Returns:
            Message object
        """
        pass

    @abstractmethod
    def parse_messages(self, messages: list) -> List[Message]:
        """Format a message in provider-specific format into a Message object.
        
        Args:
            messages: The list of messages in provider-specific format
            
        Returns:
            List of Message objects
        """
        pass