from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Type, TypeVar, Optional

from pydantic import Field, BaseModel

from llm_patch_driver.config import config
from llm_patch_driver.patch_schemas.json_patch import JsonPatch
from llm_patch_driver.patch_schemas.string_patch import StrPatch
from llm_patch_driver.tools.tool_call_schemas import ResponsesToolParam, ChatCompletionToolParam, FunctionData

if TYPE_CHECKING:
    from llm_patch_driver.driver.driver import PatchDriver

T = TypeVar("T")

# --------------------------------------------------------------------- #
# Abstract Base Class
# --------------------------------------------------------------------- #

class LLMTool(BaseModel, ABC):
    """Base class for all tools that can be used in the LLM."""

    tool_choice_reasoning: str = Field(description="Explain your reasoning here")
    provided_args_reasoning: str = Field(description="Explain your reasoning here")

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> str:
        pass

    @classmethod
    def model_dump_tool_call(cls) -> ResponsesToolParam | ChatCompletionToolParam:
        """Dump the tool call to a dictionary."""
        function_name = cls.__name__
        parameters = cls.model_json_schema()
        description = cls.__doc__ or ""
        
        match config.api_type:
            case "responses":
                return ResponsesToolParam(
                    type="function",
                    name=function_name,
                    parameters=parameters,
                    description=description.strip(),
                    strict=None
                )
            case "chat_completion":
                function_data: FunctionData = {
                    "name": function_name,
                    "parameters": parameters,
                    "description": description.strip(),
                    "strict": None
                }
                return ChatCompletionToolParam(
                    type="function",
                    function=function_data
                )
            case _:
                raise ValueError(f"Unknown tool_call_format: {config.api_type}")
    

# # --------------------------------------------------------------------- #
# # Tools for the LLM to modify the state of the object
# # --------------------------------------------------------------------- #

# class ResetToOriginalState(LLMTool):
#     """Reset the state of the object to the original state."""
#     reset_to_original_state: bool = Field(description="True if the state of the object should be reset to the original state. False if the state of the object should be modified with the other tools.")

#     async def __call__(self, patch_driver: PatchDriver) -> str:
#         patch_driver.reset_to_original_state()
#         return "The state of the object was reset to the original state."
    
# class RequestModification(LLMTool):

#     query: str = Field(description="The query to the LLM that will be used to generate a patch.")
#     context: str = Field(description="The context to the LLM that will be used to generate a patch.")

#     async def __call__(self, patch_driver: PatchDriver) -> str:
#         patch = await patch_driver.request_patch(self.query, self.context)
#         await patch_driver.apply_patch_bundle(patch)
#         return f"The following patch was generated: {patch.model_dump_json()}. It was applied to the text. Check the current state of the object to see the changes."
    
# class ModifyStateWithPatch(LLMTool):

#     patches: List[StrPatch] = Field(description="The patches to be applied to the state of the object.")

#     async def __call__(self, patch_driver: PatchDriver) -> str:
#         schema = patch_driver.patch_schema
#         bundle = schema(patches=self.patches)
#         await patch_driver.apply_patch_bundle(bundle)
#         return "The state of the object was modified with the patches."
