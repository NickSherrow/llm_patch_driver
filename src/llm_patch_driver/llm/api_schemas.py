from glom import Iter, M

RESPONSES_API_MAP = {
    "input": {
        "messages_kw": "input",
        "schema_kw": "text_format",
        "tools_kw": "tools",
        "system_prompt_dict": lambda system_prompt: {"instructions": system_prompt}
    },
    "output": {
        "parsed_object_path": "output_parsed",
        "tool_calls_path": ('output', Iter().filter(M.type == 'function_call').all()), #type: ignore[attr-defined]
        "message_path": ('output', Iter().first(M.type == 'message')) #type: ignore[attr-defined]
    },
    "tool_call_request": {
        "type_path": "type",
        "type_value": "function_call",
        "id_path": "call_id",
        "name_path": "name",
        "arguments_path": "arguments",
        "append": True
    },
    "tool_call_response": {
        "type_kw": "type",
        "type_value": "function_call_output",
        "id_kw": "call_id",
        "output_kw": "output"
    },
    "message": {
        "role_kw": "role",
        "content_kw": "content",
    }
}

COMPLETION_API_MAP = {
    "input": {
        "messages_kw": "messages",
        "schema_kw": "response_format",
        "tools_kw": "tools",
        "system_prompt_dict": lambda system_prompt: {"messages": [{"role": "system", "content": system_prompt}]}
    },
    "output": {
        "parsed_object_path": "parsed",
        "tool_calls_path": "choices.*.message.tool_calls",
        "message_path": "choices.*.message",
    },
    "tool_call_request": {
        "type_path": "type",
        "type_value": "function",
        "id_path": "id",
        "name_path": "function.name",
        "arguments_path": "function.arguments",
        "append": False
    },
    "tool_call_response": {
        "type_kw": "role",
        "type_value": "tool",
        "id_kw": "call_tool_call_id",
        "output_kw": "content"
    },
    "message": {
        "role_kw": "role",
        "content_kw": "content",
    }
}
