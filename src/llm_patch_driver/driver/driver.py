from __future__ import annotations

from typing import Dict, List, Literal, Optional, Union, cast, Type, Any, Callable, TypeVar, Generic, Coroutine

import spacy
import inspect
import json
import jsonpatch  # type: ignore[import-untyped]

from pydantic import BaseModel, Field, model_validator, PrivateAttr, ValidationError
from sortedcontainers import SortedDict
from dataclasses import dataclass

from llm_patch_driver.patch_schemas.string_patch import StrPatch, ReplaceOp, DeleteOp, InsertAfterOp
from llm_patch_driver.patch_schemas.json_patch import JsonPatch
from llm_patch_driver.patch_target.target import PatchTarget
from llm_patch_driver.tools.tools import LLMTool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_patch_driver.llm.types import ToolCallResponse, ToolCallRequest
    from llm_patch_driver.llm.wrapper import LLMClientWrapper

from .prompts import REQUEST_PATCH_PROMPT, STR_ANNOTATION_TEMPLATE, JSON_ANNOTATION_TEMPLATE, ANNOTATION_PLACEHOLDER, STR_PATCH_SYNTAX, PATCHING_LOOP_SYSTEM_PROMPT, ERROR_TEMPLATE, JSON_PATCH_SYNTAX

T = TypeVar("T", bound=Any)

# Usage:
# 1. put the object that needs to be patched into the PatchTarget
# 2. optional - add a callable to evaluate if the object is valid
# 3. create a PatchDriver with the PatchTarget

# 4a: generate a patch bundle, pass it to the PatchDriver, get a patched object
# 4b: use 'request_patch' to generate a patch, pass it to the PatchDriver, get a patched object
# 4c: use 'run_patching_loop' to run a patching loop to fix the current error

# 5. The patched object is now available as patched_object and can be used

# Limitations:
# - object body must be a string

try:
    _NLP = spacy.load("en_core_web_sm")
except OSError:
    _NLP = spacy.blank("en")
    _NLP.add_pipe("sentencizer")


# --------------------------------------------------------------------- #
# DRIVER CLASS
# --------------------------------------------------------------------- #

class PatchDriver(Generic[T]):
    """Maintains the sentence map and annotated view; applies patch bundles."""

    client: LLMClientWrapper

    def __init__(self, 
                 target_object: PatchTarget[T], 
                 current_error: str | None = None,
                 tools: List[Type[LLMTool]] = []):

        self._target_object = target_object
        self._current_error = current_error
        self._tool_map = {}
        self._tools = []
        self._cached_patch_schema = None
        self._original_state = target_object.content

        match target_object.validation_schema:
            # no schema means string data
            case None:
                self._patch_type = StrPatch
                self._patch_syntax = STR_PATCH_SYNTAX
                self._annotation_template = STR_ANNOTATION_TEMPLATE
                self._map = self._build_map(target_object.content)
                self._annotated: str = self._build_annotation(self._map)

            case _:
                self._patch_type = JsonPatch
                self._patch_syntax = JSON_PATCH_SYNTAX
                self._annotation_template = JSON_ANNOTATION_TEMPLATE
                self._annotated, self._map = self._build_json_annotation_and_map(target_object.content)

        driver_tools = self._build_tools() + tools

        for tool in driver_tools:
            self.bind_tool(tool)

    # --------------------------------------------------------------------- #
    # core public API
    # --------------------------------------------------------------------- #
    @property
    def patched_content(self) -> str:
        return self._target_object.content
    
    @property
    def original_content(self) -> str:
        return self._original_state
    
    @property
    def patched_object(self) -> T:
        return self._target_object.object
    
    @property
    def patch_schema(self) -> Type[PatchBundle]:
        """Return patch model classes augmented with *context-aware* validators."""

        if not self._cached_patch_schema:
            parent = self

            class ModdedPatchBundle(BaseModel):

                patches: List[parent._patch_type] # type: ignore[valid-type]

                __doc__ = f"Patch bundle. Syntax: {parent._patch_syntax}"

                @model_validator(mode="after")
                def _check_ids(cls, v):
                    id_map = parent._map

                    for patch in v.patches:

                        if isinstance(patch, StrPatch):
                            if not patch.tids:
                                raise ValueError("Patch must contain at least one tid")

                            for line, sent in patch._parsed_tids:
                                if line not in id_map:
                                    raise ValueError(f"Line {line} does not exist")

                                if sent not in id_map[line]:
                                    raise ValueError(f"Sentence {sent} does not exist in line {line}")
                        elif isinstance(patch, JsonPatch):
                            if not patch.a_id:
                                raise ValueError("Patch must contain an attribute id")

                            if patch.a_id not in id_map:
                                raise ValueError(f"Attribute {patch.a_id} does not exist")
                        else:
                            raise ValueError("Unsupported patch type")
                    return v
                        
            self._cached_patch_schema = cast(Type[PatchBundle], ModdedPatchBundle)

        return self._cached_patch_schema
    
    async def run_patching_loop(self, message_history: List[Any]):
        """Run a patching loop to fix the current error."""

        # tldr: 
        # - patching prompt is being added on top of the message history
        # - LLM generates patches to fix the error
        # - patches are applied to the object
        # - continue until the error is fixed

        loop_prompt = PATCHING_LOOP_SYSTEM_PROMPT.format(patch_syntax=self._patch_syntax)
        messages = message_history + [self.client.to_llm_message(loop_prompt, "system")]
        state_id = 0

        while self._current_error:
            # run LLM with current data state + error message
            annotated_state = self._annotation_template.format(text=self._annotated)
            temp_err_msg = ERROR_TEMPLATE.format(state_id=state_id, error_message=self._current_error, annotated_state=annotated_state)

            tool_calls, message = await self.client.create_message(
                messages=messages + [self.client.to_llm_message(temp_err_msg, "system")], 
                tools=self._tools
            )

            # remove current state and keep only error message in the message history
            perm_err_msg = ERROR_TEMPLATE.format(state_id=state_id, error_message=self._current_error, annotated_state=ANNOTATION_PLACEHOLDER)
            messages.extend([self.client.to_llm_message(perm_err_msg, "system"), message])

            state_id += 1

            raw_tool_data = []

            for tool_call in tool_calls:
                tool_func = self._tool_map[tool_call.name]

                try:
                    tool_args = json.loads(tool_call.arguments)
                    raw_tool_response = await tool_func(**tool_args)(patch_driver=self)

                except Exception as e:
                    raise ValueError(f"Error calling tool {tool_call.name}: {e}") from e

                tool_response = {
                    "type": tool_call.type,
                    "id": tool_call.id,
                    "content": raw_tool_response
                }

                raw_tool_data.append((tool_call, tool_response))
            
            # patch driver doesn't know what tool calling API is being used, so we format outputs inside the client wrapper
            formatted_tool_data = self.client.format_tool_call_results(raw_tool_data, message)
            messages.extend(formatted_tool_data)

            # run validation to decide if we should continue the loop
            self._current_error = await self._target_object.validate_content()

    # --------------------------------------------------------------------- #
    # advanced public API
    # --------------------------------------------------------------------- #

    async def request_patch(self, query: str, context: str) -> PatchBundle:
        """Request a patch from the LLM."""

        template = REQUEST_PATCH_PROMPT + "\n" + self._patch_syntax
        prompt = template.format(query=query, context=context, text=self._annotated)
        patch = await self.client.create_object(
            schema=self.patch_schema, 
            messages=[self.client.to_llm_message(prompt, "system")]
        )
        
        return patch

    async def apply_patch_bundle(self, bundle: PatchBundle):
        """Mutates internal map with *bundle* and refreshes the annotation."""

        sorted_patches = self._sort_patches(bundle.patches)

        for patch in sorted_patches:
            self._apply_patch(patch)

        match self._patch_type.__name__:

            case StrPatch.__name__:
                # string patches modify the map so we update the target object and generate a new annotation
                self._target_object.content = self._assemble_text()
                self._annotated = self._build_annotation(self._map)

            case JsonPatch.__name__:
                # json patches modify the object directly but we need both new map and annotation
                self._annotated, self._map = self._build_json_annotation_and_map(self._target_object.content)

    def bind_tool(self, tool: Type[LLMTool]):
        """Add a tool to the patch driver."""

        self._tools.append(tool.model_dump_tool_call())
        self._tool_map[tool.__name__] = tool
        
    def reset_to_original_state(self):
        """Reset the object to the original state."""

        match self._patch_type.__name__:

            case StrPatch.__name__:
                self._target_object.content = self._original_state
                self._map = self._build_map(self._original_state)
                self._annotated = self._build_annotation(self._map)

            case JsonPatch.__name__:
                self._target_object.content = self._original_state
                self._annotated, self._map = self._build_json_annotation_and_map(self._target_object.content)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    @staticmethod
    def _build_map(text: str) -> SortedDict:
        """Single pass through spaCy (via ``nlp.pipe``) to populate the map."""
        sent_map: SortedDict = SortedDict()
        lines = text.splitlines()
        for line_idx, doc in enumerate(_NLP.pipe(lines), start=1):
            # Keep sentences exactly as they appear in the original text.
            line_sents: List[str] = [s.text for s in doc.sents] or [lines[line_idx - 1]]
            sent_map[line_idx] = SortedDict({sid: s for sid, s in enumerate(line_sents, start=1)})
        return sent_map

    @staticmethod
    def _build_annotation(sentence_map: SortedDict) -> str:
        annotated_parts: List[str] = []
        for line_id, line_map in sentence_map.items(): 
            for sent_id, sent in line_map.items():            
                annotated_parts.append(f"<tid={line_id}_{sent_id}>{sent}</tid>")
        return "\n".join(annotated_parts)
    
    @staticmethod
    def _build_json_annotation_and_map(
        data: Any,
        _attr_idx_start: int = 1,
        _item_idx_start: int = 1,
        _path: str = "",
        _attr_map: Optional[SortedDict] = None,
    ) -> tuple[Any, SortedDict]:
        """Return an annotated deep-copy of *data* together with an id→path map."""

        if _attr_map is None:
            # Use SortedDict to keep attribute ids ordered consistently across recursion levels
            _attr_map = SortedDict()

        def _json_pointer(parent: str, token: str | int) -> str:
            """Build a JSON Pointer by appending *token* to *parent*."""
            # Per RFC 6901 we need to escape '~' and '/' in reference tokens.
            if isinstance(token, str):
                token = token.replace('~', '~0').replace('/', '~1')
            return f"{parent}/{token}" if parent else f"/{token}"

        # -- dict ----------------------------------------------------------- #
        if isinstance(data, dict):
            annotated_dict: SortedDict = SortedDict()
            attr_idx = _attr_idx_start
            for key, value in data.items():
                annotated_key = f"<a={attr_idx} k={key}>"
                _attr_map[attr_idx] = _json_pointer(_path, key)
                annotated_value, _ = PatchDriver._build_json_annotation_and_map(
                    value,
                    _attr_idx_start=attr_idx + 1,
                    _item_idx_start=1,
                    _path=_json_pointer(_path, key),
                    _attr_map=_attr_map,
                )

                attr_idx = max(_attr_map.keys()) + 1
                annotated_dict[annotated_key] = annotated_value

            return annotated_dict, _attr_map

        # -- list ----------------------------------------------------------- #
        if isinstance(data, list):
            annotated_list: List[Any] = []
            item_idx = _item_idx_start
            for element in data:
                if isinstance(element, (dict, list)):
                    next_free_id = max(_attr_map.keys()) + 1 if _attr_map else _attr_idx_start
                    annotated_element, _ = PatchDriver._build_json_annotation_and_map(
                        element,
                        _attr_idx_start=next_free_id,
                        _item_idx_start=1,
                        _path=_json_pointer(_path, item_idx - 1),
                        _attr_map=_attr_map,
                    )
                else:
                    annotated_element = f"<i={item_idx} v={element}>"

                annotated_list.append(annotated_element)
                item_idx += 1

            return annotated_list, _attr_map

        return data, _attr_map
    
    def _build_tools(self) -> List[Type[LLMTool]]:
        """Build tools for the patch driver."""

        # tools are built based on what type of patch is needed
        # we do that because LLMs love determinism in schemas and docstrings
    
        match self._patch_type.__name__:
            case StrPatch.__name__:
                reset_doc = "Reset the state of the object to the original state."
                modify_doc = "Modify the state of the object with the patches."
                request_doc = "Request a modification to the state of the object."

            case JsonPatch.__name__:
                reset_doc = "Reset the state of the object to the original state."
                modify_doc = "Modify the state of the object with the patches."
                request_doc = "Request a modification to the state of the object."

            case _:
                raise ValueError("Not implemented for non-string target data")

        parent = self

        class ResetToOriginalState(LLMTool):
            reset_to_original_state: bool = Field(description="True if the state of the object should be reset to the original state. False if the state of the object should be modified with the other tools.")

            __doc__ = f"{reset_doc}"

            async def __call__(self) -> str:
                parent.reset_to_original_state()
                return "The state of the object was reset to the original state."
            
        class RequestModification(LLMTool):

            query: str = Field(description="The query to the LLM that will be used to generate a patch.")
            context: str = Field(description="The context to the LLM that will be used to generate a patch.")

            __doc__ = f"{request_doc}"

            async def __call__(self) -> str:
                patch = await parent.request_patch(self.query, self.context)
                await parent.apply_patch_bundle(patch)
                return f"The following patch was generated: {patch.model_dump_json()}. It was applied to the text. Check the current state of the object to see the changes."
            
        class ModifyStateWithPatch(LLMTool):

            patches: List[self._patch_type] = Field(description="The patches to be applied to the state of the object.") # type: ignore[valid-type]

            __doc__ = f"{modify_doc}"

            async def __call__(self) -> str:
                schema = parent.patch_schema
                bundle = schema(patches=self.patches)
                await parent.apply_patch_bundle(bundle)
                return "The state of the object was modified with the patches."
            
        return [ResetToOriginalState, RequestModification, ModifyStateWithPatch]
    
    def _assemble_text(self) -> str:
        """Re-assemble the current map back into raw multi-line text."""
        lines: List[str] = []
        for line_id, line_map in self._map.items():  
            sents = [line_map[sid] for sid in line_map]      
            lines.append("".join(sents))
        return "\n".join(lines)
    
    def _sort_patches(self, patches: List[StrPatch]) -> List[StrPatch]:
        """Sort patches to keep coordinate validity: replacements first, then deletes, then inserts."""
        
        priority = {
            "replace": 0,
            "delete": 1,
            "insert_after": 2,
        }

        def _anchor_line(patch: StrPatch) -> int:
            anchor_tid = patch.tids[-1] if patch.operation.type == "insert_after" else patch.tids[0]
            return int(anchor_tid.split("_")[0])

        # Sort patches to keep coordinate validity: replacements first, then deletes, then inserts.
        sorted_patches = sorted(
            patches,
            key=lambda p: (priority.get(p.operation.type, 99), -_anchor_line(p)),
        )
        return sorted_patches
    
    def _apply_patch(self, patch: StrPatch | JsonPatch) -> None:
        """Apply a patch to the current state of the object."""

        match patch:

            # -- string patch -------------------------------------------------- #
            case StrPatch():

                match patch.operation:
                    # -- replace -------------------------------------------------- #
                    case ReplaceOp(pattern=pat, replacement=repl):
                        for line, sent in patch._parsed_tids:
                            segment: str = self._map[line][sent]
                            self._map[line][sent] = segment.replace(pat, repl)

                    # -- delete --------------------------------------------------- #
                    case DeleteOp():
                        for line, sent in sorted(patch._parsed_tids, key=lambda x: (x[0], x[1]), reverse=True):
                            line_map = self._map[line]
                            del line_map[sent]
                            for sid in sorted([k for k in line_map if k > sent]):
                                line_map[sid - 1] = line_map.pop(sid)

                            if not line_map:
                                del self._map[line]
                                for idx in range(line + 1, max(self._map.keys(), default=line) + 1):
                                    if idx in self._map:
                                        self._map[idx - 1] = self._map.pop(idx)

                    # -- insert after ------------------------------------------- #
                    case InsertAfterOp(text=text):
                        anchor_line, _ = patch._parsed_tids[-1]

                        max_line = max(self._map) if self._map else 0
                        for idx in range(max_line, anchor_line, -1):
                            self._map[idx + 1] = self._map[idx]

                        new_line_id = anchor_line + 1
                        doc = _NLP(text)
                        sents = [s.text for s in doc.sents] or [text]
                        self._map[new_line_id] = SortedDict({sid: s for sid, s in enumerate(sents, start=1)})

                    case _:
                        raise ValueError(f"Unsupported patch type: {patch}")

            # -- json patch -------------------------------------------------- #
            case JsonPatch():

                path = self._map[patch.a_id]

                if patch.i_id is not None:
                    path = f"{path}/{patch.i_id - 1}"  

                match patch.op:
                    case "replace":
                        op_dict = {"op": "replace", "path": path, "value": patch.value}

                    case "add":
                        op_dict = {"op": "add", "path": path, "value": patch.value}

                    case "remove":
                        op_dict = {"op": "remove", "path": path}

                    case _:
                        raise ValueError(f"Unsupported patch type: {patch}")
                    
                patch_obj = jsonpatch.JsonPatch([op_dict])
                patch_obj.apply(self._target_object.content, in_place=True)
            
class PatchBundle(BaseModel):
    patches: List[StrPatch]