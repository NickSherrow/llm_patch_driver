from typing_extensions import TypedDict, NotRequired, Callable

class OutputMap(TypedDict):
    parsed_object_path: str
    tool_calls_path: str | tuple
    message_path: str | tuple

class InputMap(TypedDict):
    messages_kw: str
    schema_kw: str
    tools_kw: str
    system_prompt_dict: Callable

class ToolCallRequestMap(TypedDict):
    type_path: str
    type_value: str
    id_path: str
    name_path: str
    arguments_path: str
    append: bool

class ToolCallResponseMap(TypedDict):
    type_kw: str
    type_value: str
    id_kw: str
    output_kw: str

class MessageMap(TypedDict):
    role_kw: str
    content_kw: str

class ApiLLMMap(TypedDict):
    input: InputMap
    output: OutputMap
    tool_call_request: ToolCallRequestMap
    tool_call_response: ToolCallResponseMap
    message: MessageMap

