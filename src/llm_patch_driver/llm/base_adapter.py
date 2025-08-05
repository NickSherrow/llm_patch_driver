"""Base adapter for LLM API providers.

This module defines the abstract interface that all LLM API adapters must implement.
Adapters handle the provider-specific details of:
- Building API requests from standardized inputs
- Parsing API responses into standardized outputs  
- Formatting messages and tool calls according to provider schemas
"""

from __future__ import annotations

import inspect
from functools import partial

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Callable

from pydantic import BaseModel

from llm_patch_driver.llm.types import ToolCallRequest, ToolCallResponse, Message

U = TypeVar("U", bound=BaseModel)


class BaseApiAdapter(ABC):
    """Abstract base class for LLM API adapters.
    
    Each concrete adapter implements provider-specific logic for:
    1. Converting standardized inputs into provider-specific API calls
    2. Parsing provider responses into standardized internal types
    3. Formatting messages and tool interactions according to provider schemas
    
    This abstraction allows the LLMClientWrapper to work with any LLM provider
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
    def format_tool_results(
        self, 
        tool_calls: List[ToolCallResponse]
        ) -> List[dict]:
        """Format tool call results for inclusion in message history.
        
        Args:
            tool_calls: List of (request, response) pairs for executed tool calls
            
        Returns:
            List of formatted message objects ready to add to conversation history
        """
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
    def parse_object_from_llm_output(self, raw_response: Any) -> U:
        """Parse an object from the LLM API into a Pydantic object.
        
        Args:
            raw_response: Raw response object from the LLM API
            
        Returns:
            Pydantic or JSON object
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