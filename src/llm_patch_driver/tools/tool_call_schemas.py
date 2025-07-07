from typing import TypedDict, Required, Optional, Dict, Literal


# --------------------------------------------------------------------- #
# Core Function Data
# --------------------------------------------------------------------- #

class FunctionData(TypedDict, total=False):
    name: Required[str]
    """The name of the function to call."""

    parameters: Required[Dict[str, object]]
    """The parameters the functions accepts, described as a JSON Schema object."""

    strict: Required[Optional[bool]]
    """Whether to enable strict schema adherence when generating the function call.

    If set to true, the model will follow the exact schema defined in the
    `parameters` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. Learn more about Structured Outputs in the
    [function calling guide](docs/guides/function-calling).
    """

    description: Optional[str]
    """A description of the function.

    Used by the model to determine whether or not to call the function.
    """

# --------------------------------------------------------------------- #
# Wrappers for different APIs
# --------------------------------------------------------------------- #

class ResponsesToolParam(FunctionData):
    type: Required[Literal["function"]]
    """The type of the function tool. Always `function`."""


class ChatCompletionToolParam(TypedDict, total=False):
    type: Required[Literal["function"]]
    """The type of the function tool. Always `function`."""

    function: Required[FunctionData]
    """The function to call."""

