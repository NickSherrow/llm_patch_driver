from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Type, TypeVar, Optional

from pydantic import Field, BaseModel
from llm_patch_driver.llm.schemas import ToolSchema

T = TypeVar("T")

class LLMTool(BaseModel, ABC): #TODO: allow to pass args at runtime
    """Base class for all tools that can be used in the LLM.
    
    Notes:
    - the tool is being called using __call__ method
    - all args that are required from the LLM must be defined as class attributes
    """

    tool_choice_reasoning: str = Field(description="Explain your reasoning here")
    provided_args_reasoning: str = Field(description="Explain your reasoning here")

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> str:
        pass

    @classmethod
    def model_dump_tool_schema(cls) -> ToolSchema:
        """Dump the tool call to a standard schema."""
        function_name = cls.__name__
        parameters = cls.model_json_schema()
        description = cls.__doc__ or ""

        schema = ToolSchema(
            name=function_name,
            parameters=parameters,
            description=description.strip(),
            strict=False,
            type="function"
        )

        return schema
