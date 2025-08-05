from dataclasses import dataclass
from pydantic import BaseModel
from typing import List

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
    content: str | list | dict
    tool_calls: List[ToolCallRequest] = []
    attached_object: BaseModel | str | dict | None = None