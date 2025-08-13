from __future__ import annotations

import inspect
import json
from typing import List, Optional, Type, Any, Callable, TypeVar, Generic

from pydantic import BaseModel, Field

from llm_patch_driver.llm.base_adapter import BaseApiAdapter
from llm_patch_driver.llm.schemas import ToolCallResponse, Message
from llm_patch_driver.patch.base_patch import PatchBundle
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.llm.base_tool import LLMTool
from llm_patch_driver.driver.prompts import REQUEST_PATCH_PROMPT, PATCHING_LOOP_SYSTEM_PROMPT
from llm_patch_driver.llm import OpenAIChatCompletions

T = TypeVar("T", bound=Any)
U = TypeVar("U", bound=BaseModel)

class PatchDriver(Generic[T]):
    """Orchestrates patching process.

    Handles the following:
    - Core LLM calls and tool execution.
    - Agentic loop to iteratively fix the error.
    - Patch generation from query or patch bundle.

    Args:
    - **target_object**: The ``PatchTarget[T]`` to operate on. Holds content,
      annotation, validation logic, and patch application behavior.
    - **create_method**: Callable used to create an LLM response when no
      structured object is required (e.g., plain chat completion). May be sync
      or async.
    - **parse_method**: Callable used to parse an LLM response when structured
      output (``schema``) is requested. May be sync or async.
    - **model_args**: Optional provider/model-specific kwargs forwarded to the
      adapter on each LLM call.
    - **api_adapter**: Concrete implementation of ``BaseApiAdapter`` that
      formats inputs and parses outputs for the chosen LLM API.
    - **tools**: Optional list of ``LLMTool`` classes to pre-bind. When not
      provided, a default set is registered (reset, query-driven modification,
      direct patch application) and adjusted to the active patch type.
    - **max_cycles**: Upper bound of iterations in the patching loop to prevent
      unbounded retries.

    Methods:
    - ``run_patching_loop(message_history)``: Runs the iterative loop; executes
      LLM-emitted tool calls and re-validates after each cycle until the target
      becomes valid or ``max_cycles`` is reached.
    - ``request_patch_bundle(query, context)``: Requests a ``PatchBundle`` from
      the LLM given the annotated content and developer-provided context.
    - ``bind_tool(tool)``: Registers a tool class. Its schema is adapted via the
      active ``api_adapter`` so the LLM can invoke it.

    Notes:
    - All modifications happen in place on ``target_object``. The target
      maintains a backup, annotations, and the id→content lookup map used by
      patches.
    - The driver is adapter-agnostic and relies on the supplied
      ``create_method``/``parse_method`` to support both chat-only and
      structured-output interactions.
    """

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
                    tool_instance = tool_func.model_validate(
                        tool_args, 
                        context={"id_content_map": object_to_patch._lookup_map}
                        )
                    raw_tool_response = await tool_instance()

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
        
        request_schema = object_to_patch.patch_type.get_bundle_schema()
        
        message = await self.call_llm(
            schema=request_schema, 
            messages=[Message(role="system", content=prompt)]
        )

        patch_bundle = request_schema.model_validate(
            message.attached_object, 
            context={"id_content_map": object_to_patch._lookup_map}
            )
        
        return patch_bundle

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
        bundle_schema = object_to_patch.patch_type.get_bundle_schema()
        parent = self

        class ResetToOriginalState(LLMTool):
            """Reset the corrupted response to it's original state before your modifications.
            
            Use this tool if your fixing process went wrong and you need to start over."""
            
            reset_to_original_state: bool = Field(description="True if the state of the object should be reset to the original state. False if the state of the object should be modified with the other tools.")

            async def __call__(self) -> str:
                await object_to_patch.reset_to_original_state()
                return "The state of the object was reset to the original state."
            
        class ModifyWithQuery(LLMTool):
            """Request a specific modification to the corrupted response from another LLM.

            Use this tool if the modification is too complex.

            Notes:
            - The LLM will not see the original task! It will only receive the annotated
            version of the corrupted response, your query and any information you add to 
            the query as context.
            - To get good results, carefully craft the plan of the required modification.
            Explain in details what needs to be done. Remember, the only context is available
            to the LLM is the annotated version of the corrupted response, your plan, and 
            the context you provide.
            """

            plan: str = Field(description="The detailed and thoughtful plan of the required modification in Markdown format.")
            context: str = Field(description="Any supportive information that would help LLM deliver the required modification.")

            async def __call__(self) -> str:
                patch_bundle = await parent.request_patch_bundle(self.plan, self.context)
                await object_to_patch.apply_patches(patch_bundle.patches)
                return f"The following patch was generated: {patch_bundle.model_dump_json()}. It was applied to the text. Check the current state of the object to see the changes."
            
        class ModifyWithPatch(LLMTool):
            """Generate a patch that would fix the corrupted response.
            
            Use this tool if you have a good idea of what needs to be done, and you can
            express this idea as a patch.

            Notes:
            - Each patch requires a lot of thinking and planning. If you decide to use this tool,
            be verbose in your reasoning. Provide as much details as possible.
            - Be careful to the patch syntax.
            """

            provided_patch_bundle: bundle_schema = Field(description="The patches to be applied to the state of the object.") # type: ignore[valid-type]

            async def __call__(self) -> str:
                patches = self.provided_patch_bundle.patches
                await object_to_patch.apply_patches(patches)
                return "The state of the object was modified with the patches."
            
        return [ResetToOriginalState, ModifyWithQuery, ModifyWithPatch]