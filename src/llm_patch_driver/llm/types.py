from dataclasses import dataclass
from typing import List

@dataclass
class ToolCallRequest:
    type: str
    id: str
    name: str
    arguments: str

@dataclass
class ToolCallResponse:
    type: str
    id: str
    output: str

@dataclass
class Message:
    role: str
    content: str | list | dict