from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, TypedDict


class FunctionData(TypedDict):
    """Structure describing a single function for chat completion APIs."""

    name: str
    parameters: dict[str, Any]
    description: str
    strict: Optional[bool]


@dataclass
class ResponsesToolParam:
    """Minimal schema for the Responses API tool representation."""

    type: str
    name: str
    parameters: dict[str, Any]
    description: str
    strict: Optional[bool] = None


@dataclass
class ChatCompletionToolParam:
    """Minimal schema for the Chat Completion API tool representation."""

    type: str
    function: FunctionData

