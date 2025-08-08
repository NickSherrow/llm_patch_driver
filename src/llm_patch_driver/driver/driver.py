from __future__ import annotations

import inspect
import json
import jsonpatch
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union, cast, Type, Any, Callable, TypeVar, Generic, Coroutine

import spacy
from pydantic import BaseModel, Field, model_validator, PrivateAttr, ValidationError
from sortedcontainers import SortedDict

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import ToolCallRequest, ToolCallResponse, Message
from llm_patch_driver.patch.base_patch import PatchBundle, BasePatch
from llm_patch_driver.patch.json.json_patch import JsonPatch
from llm_patch_driver.patch.string.string_patch import ReplaceOp, DeleteOp, InsertAfterOp, StrPatch
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.llm.base_tool import LLMTool
from llm_patch_driver.driver.prompts import REQUEST_PATCH_PROMPT, PATCHING_LOOP_SYSTEM_PROMPT
from llm_patch_driver.config import config
from llm_patch_driver.llm import OpenAIChatCompletions

from llm_patch_driver.logging import log_wrapper, OutputFormat, ArgSpec, ArgLogData, LogData

collector = config.build_log_collector(__name__)

T = TypeVar("T", bound=Any)
U = TypeVar("U", bound=BaseModel)

class PatchDriver(Generic[T]):
    """Maintains the sentence map and annotated view; applies patch bundles."""

    def __init__(
        self,
        target_object: PatchTarget[T],
        create_method: Callable,
        parse_method: Callable,
        model_args: dict | None = None,
        api_adapter: BaseApiAdapter = OpenAIChatCompletions(),
        tools: List[Type[LLMTool]] | None = None,
        max_cycles: int = 25,
    ):
        
        self.api_adapter = api_adapter
        self.target_object = target_object

        self._create_method = create_method
        self._parse_method = parse_method
        self._model_args = model_args if model_args is not None else {}
        self._max_cycles = max_cycles

        # prompts prebuilt

        loop_prompt = PATCHING_LOOP_SYSTEM_PROMPT.format(
            patch_syntax=self.target_object.patch_type.prompts.syntax
            )
        loop_prompt_message = Message(
            role="system",
            content=loop_prompt
            )
        
        self._loop_prompt_message = loop_prompt_message
        self._request_prompt = (REQUEST_PATCH_PROMPT + "\n" + self.target_object.patch_type.prompts.syntax)

        self._tool_map = {} # lookup table tool_name:tool
        self._tools = [] # list of tool schemas to be passed to the LLM

        driver_tools = self._build_tools() + [] if tools is None else tools

        for tool in driver_tools:
            self.bind_tool(tool)

    # --------------------------------------------------------------------- #
    # core public API
    # --------------------------------------------------------------------- #
    
    async def run_patching_loop(self, message_history: List[Any]):
        """Run a patching loop to fix the current error.

        Args:
            message_history: List of messages that led to an error including the corrupted output.

        Usage recommendation:
            The problem is sophisticated and multiple iterations are needed to fix it.

        Notes:
            - All modifications are done in place.
            - We pass message history that led to an error on top of all prompts 
            to let the model keep the context.
            - Each iteration the model is being asked to use tools to fix the error.
            - The loop is terminated when the error is fixed.
        """

        # TODO: trim message history if it's getting too long

        original_messages = self.api_adapter.parse_messages(message_history)
        object_to_patch = self.target_object
        current_messages = original_messages + [self._loop_prompt_message]

        num_cycles = 0
        while object_to_patch.current_error:
            # run LLM with current data state + error message
            message = await self.call_llm(
                messages=current_messages + [object_to_patch.debugging_message], 
                tools=self._tools
            )

            # remove current state and keep only error message in the message history
            current_messages.extend(
                [object_to_patch.debugging_message_placeholder, message]
                )

            for tool_call in message.tool_calls:
                tool_func = self._tool_map[tool_call.name]

                try:
                    tool_args = json.loads(tool_call.arguments)
                    raw_tool_response = await tool_func(**tool_args)()

                except Exception as e:
                    raise ValueError(f"Error calling tool {tool_call.name}: {e}") from e
                
                tool_response = ToolCallResponse(
                    request=tool_call, 
                    type=tool_call.type, 
                    id=tool_call.id, 
                    output=raw_tool_response
                    )

                current_messages.append(tool_response) #type: ignore[arg-type]
            
            # run validation to decide if we should continue the loop
            object_to_patch.current_error = await object_to_patch.validate_content()

            num_cycles += 1
            if num_cycles >= self._max_cycles and object_to_patch.current_error:
                raise ValueError(f"Patching loop reached max cycles ({self._max_cycles}). Stopping.")

    # --------------------------------------------------------------------- #
    # advanced public API
    # --------------------------------------------------------------------- #

    async def request_patch_bundle(self, query: str, context: str) -> PatchBundle:
        """Request a patch from the LLM to fix the current error.
        
        Args:
            query: The query to the LLM that will be used to generate a patch.
            context: The context to the LLM that will be used to generate a patch.

        Usage recommendation:
            The problem is simple and a single patch is enough to fix it, or
            developer wants to have more control over the patching context.
        """

        object_to_patch = self.target_object

        prompt = self._request_prompt.format(
            query=query, 
            context=context, 
            text=object_to_patch.annotated_content
            )
        
        request_schema = object_to_patch.patch_type.build_bundle_schema(object_to_patch._lookup_map)
        
        message = await self.call_llm(
            schema=request_schema, 
            messages=[Message(role="system", content=prompt)]
        )
        
        return cast(PatchBundle, message.attached_object)

    def bind_tool(self, tool: Type[LLMTool]):
        """Add a tool to the patch driver.
        
        Args:
            tool: The tool to add to the patch driver.

        Usage recommendation:
            If fixing process requires 3rd party data, developer can build their own tools
            to access this data.
        """

        schema = tool.model_dump_tool_schema()
        formatted_schema = self.api_adapter.format_tool_schema(schema)

        self._tools.append(formatted_schema)
        self._tool_map[tool.__name__] = tool

    # --------------------------------------------------------------------- #
    # Internal LLM handling
    # --------------------------------------------------------------------- #

    @log_wrapper(
        log_input=[
            ArgSpec(name="messages", logger_level="INFO", otel_attribute="input"),
            ArgSpec(name="tools", logger_level="INFO", otel_attribute="metadata")
            ], 
            log_output=OutputFormat(otel_output=True, logger_level="INFO"),
            span_kind="llm")
    async def call_llm(
        self,
        messages: List[Message], 
        tools: Optional[List[dict]] = None, 
        system_prompt: Optional[str] = None,
        schema: Optional[Type[U]] = None
        ) -> Message:
        """Create a message from the LLM.
        
        Args:
            messages: List of messages to be passed to the LLM.
            tools: List of tools to be passed to the LLM.
            system_prompt: System prompt to be passed to the LLM.
            schema: Schema to be passed to the LLM.
        """
        
        # Format inputs using the adapter
        llm_call_input = self.api_adapter.format_llm_call_input(
            messages=messages,
            tools=tools,
            system_prompt=system_prompt,
            schema=schema
        )
        
        # Add model args
        llm_call_input.update(self._model_args)

        is_object_required = schema is not None
        is_create_async = inspect.iscoroutinefunction(self._create_method)
        is_parse_async = inspect.iscoroutinefunction(self._parse_method)

        match (is_object_required, is_create_async, is_parse_async):

            case (True, _, True):
                raw_response = await self._parse_method(**llm_call_input)
    
            case (True, _, False):
                raw_response = self._parse_method(**llm_call_input)

            case (False, True, _):
                raw_response = await self._create_method(**llm_call_input)

            case (False, False, _):
                raw_response = self._create_method(**llm_call_input)
        
        # Parse response using adapter
        message = self.api_adapter.parse_llm_output(raw_response)
        
        return message


    def _build_tools(self) -> List[Type[LLMTool]]:
        """Build tools for the patch driver.
        
        Notes:
            PatchDriver dynamically builds tools from presets to customize docstrings,
            and adjust args schemas to the current patch type.
        """

        object_to_patch = self.target_object
        bundle_schema = object_to_patch.patch_type.build_bundle_schema(object_to_patch._lookup_map)
        parent = self

        reset_doc = object_to_patch.patch_type.prompts.reset_tool_doc
        request_doc = object_to_patch.patch_type.prompts.request_tool_doc
        modify_doc = object_to_patch.patch_type.prompts.modify_tool_doc

        class ResetToOriginalState(LLMTool):
            
            reset_to_original_state: bool = Field(description="True if the state of the object should be reset to the original state. False if the state of the object should be modified with the other tools.")

            __doc__ = f"{reset_doc}"

            async def __call__(self) -> str:
                await object_to_patch.reset_to_original_state()
                return "The state of the object was reset to the original state."
            
        class RequestModification(LLMTool):

            query: str = Field(description="The query to the LLM that will be used to generate a patch.")
            context: str = Field(description="The context to the LLM that will be used to generate a patch.")

            __doc__ = f"{request_doc}"

            async def __call__(self) -> str:
                patch_bundle = await parent.request_patch_bundle(self.query, self.context)
                await object_to_patch.apply_patches(patch_bundle.patches)
                return f"The following patch was generated: {patch_bundle.model_dump_json()}. It was applied to the text. Check the current state of the object to see the changes."
            
        class ModifyStateWithPatch(LLMTool):

            provided_patch_bundle: bundle_schema = Field(description="The patches to be applied to the state of the object.") # type: ignore[valid-type]

            __doc__ = f"{modify_doc}"

            async def __call__(self) -> str:
                patches = self.provided_patch_bundle.patches
                await object_to_patch.apply_patches(patches)
                return "The state of the object was modified with the patches."
            
        return [ResetToOriginalState, RequestModification, ModifyStateWithPatch]