"""To make internal logic readable, we use a set of dataclasses for core LLM abstractions."""

from dataclasses import dataclass, field
from typing import List
import json

from pydantic import BaseModel
from rich.json import JSON
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import RenderableType, Console, Group

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

    @property
    def rich_renderable(self) -> RenderableType:
        """Return a rich renderable type for the tool call request."""
        rendered_tool_call = JSON(self.arguments)
        return Panel(
            rendered_tool_call, 
            title=f"Calling: {self.name}", 
            style="magenta"
        )

@dataclass
class ToolCallResponse:
    request: ToolCallRequest
    type: str
    id: str
    output: str

    @property
    def rich_renderable(self) -> RenderableType:
        """Return a rich renderable type for the tool call response."""
        return Panel(
            Markdown(self.output, style="white"),
            title=f"Response from: {self.request.name}",
            style="white"
        )

@dataclass
class Message:
    role: str
    content: str | list | dict | None = None
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    attached_object: BaseModel | str | dict | None = None


    @property
    def rich_renderable(self) -> RenderableType:
        """Return a rich renderable type for the message."""

        panels = []

        if self.tool_calls:
            panels.extend([tool_call.rich_renderable for tool_call in self.tool_calls])

        text_color = coloring_map.get(self.role, "white")

        match self.content:

            case str():
                content = Markdown(self.content, style=text_color)

                panels.append(
                    Panel(content, title=self.role, style=text_color)
                    )
            
            case list() | dict():
                try:
                    content = json.dumps(self.content, indent=4)
                    content = JSON(content)
                
                except Exception:
                    content = str(self.content)
                    content = Markdown(content, style=text_color)

                panels.append(
                    Panel(content, title=self.role, style=text_color)
                    )

        return Group(*panels)


@dataclass
class ToolSchema:
    name: str
    parameters: dict
    description: str
    strict: bool
    type: str

def parse_history_to_rich_renderable(history: List[Message | ToolCallResponse] | Message | ToolCallResponse) -> RenderableType:
    """Parse the history to a list of rich renderable types."""
    if not isinstance(history, list):
        history = [history]

    return Group(*[item.rich_renderable for item in history])