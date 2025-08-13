"""To make internal logic readable, we use a set of dataclasses for core LLM abstractions."""

from dataclasses import dataclass, field
from typing import List

from pydantic import BaseModel

coloring_map = {
    "system": "blue",
    "user": "green",
    "assistant": "white",
    "tool": "magenta",
}

@dataclass
class ToolCallRequest:
    type: str
    id: str
    name: str
    arguments: str

@dataclass
class ToolCallResponse:
    request: ToolCallRequest
    type: str
    id: str
    output: str

@dataclass
class Message:
    role: str
    content: str | list | dict | None = None
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    attached_object: BaseModel | str | dict | None = None

@dataclass
class ToolSchema:
    name: str
    parameters: dict
    description: str
    strict: bool
    type: str
