from __future__ import annotations

from typing import Generic, Type, Callable, Optional, Coroutine, Any, TypeVar, List, Dict, cast
from pydantic import BaseModel, model_validator, ValidationError, PrivateAttr
from sortedcontainers import SortedDict
from copy import deepcopy
import inspect

from .prompts import ERROR_TEMPLATE
from llm_patch_driver.llm.schemas import Message
from llm_patch_driver.patch.base_patch import BasePatch

T = TypeVar("T")

class PatchTarget(BaseModel, Generic[T]):
    """Wrapper for a target object that needs to be patched.

    Handles the following:
    - Checks if the target object passes the validation schema or condition.
    - Annotates the target object with metadata that helps LLM to understand it better.
    - Stores backup copy of the target object to be able to reset to the original state.
    - Applies generated patches to the target object.

    Args:
    - **object**: The object to patch. If ``content_attribute`` is ``None``, the
      object itself is treated as the content. Otherwise, the named attribute of
      the object is treated as the content.
    - **patch_type**: any class that implements ``BasePatch`` interface.
    - **current_error**: Optional latest validation error string.
    - **content_attribute**: Optional attribute name indicating where the
      content lives on ``object`` when the content is nested.
    - **validation_condition**: Optional sync or async callable that receives the
      current content and returns an error message (``str``) or ``None`` if the
      content is valid.
    - **validation_schema**: Optional Pydantic model used to validate the
      content. Required when the content is not a ``str``.

    Methods:
    - ``reset_to_original_state``: resets the target object to the original state.
    - ``apply_patches``: applies a list of patches to the target object.
    - ``validate_content``: validates the target object against the validation schema or condition.

    Notes:
    - All modifications happen in place.
    """

    object: T
    patch_type: Type['BasePatch']
    current_error: str | None = None
    content_attribute: str | None = None
    validation_condition: Callable[[T], Optional[str]] | Callable[[T], Coroutine[Any, Any, Optional[str]]] | None = None
    validation_schema: Type[BaseModel] | None = None

    _backup_copy: T | None = PrivateAttr(default=None)
    _annotated: str = PrivateAttr(default="")
    _lookup_map: SortedDict = PrivateAttr(default=SortedDict())
    _iteration: int = PrivateAttr(default=0)

    def model_post_init(self, __context):
        self._backup_copy = deepcopy(self.content)
        self._lookup_map = self.patch_type.build_map(self.content)
        self._annotated = self.patch_type.build_annotation(self.content, self._lookup_map)

    @property
    def content(self) -> Any:
        if self.content_attribute is None:
            return self.object
        else:
            return getattr(self.object, self.content_attribute)
        
    @content.setter
    def content(self, value: Any) -> None:
        if self.content_attribute is None:
            self.object = value
        else:
            setattr(self.object, self.content_attribute, value)

    @property
    def annotated_content(self) -> str:
        return self.patch_type.prompts.annotation_template.format(
            object_content=str(self._annotated)
        )

    @property
    def debugging_message(self) -> Message:
        debugging_state = ERROR_TEMPLATE.format(
            state_id=self._iteration,
            error_message=self.current_error,
            annotated_state=self.annotated_content
        )

        return Message(
            role="system",
            content=debugging_state
        )
    
    @property
    def debugging_message_placeholder(self) -> Message:
        debugging_state = ERROR_TEMPLATE.format(
            state_id=self._iteration,
            error_message=self.current_error,
            annotated_state=self.patch_type.prompts.annotation_placeholder
        )

        return Message(
            role="system",
            content=debugging_state
        )
    
    async def reset_to_original_state(self) -> None:
        self.content = deepcopy(self._backup_copy)
        self._iteration = 0
        self._lookup_map = self.patch_type.build_map(self.content)
        self._annotated = self.patch_type.build_annotation(self.content, self._lookup_map)
        self.current_error = await self.validate_content()
    
    async def apply_patches(self, patches: List['BasePatch']) -> None:
        for patch in patches:
            patch.apply_patch(self)

        self.content = self.patch_type.content_from_map(self.content, self._lookup_map)

        self._iteration += 1
        self._lookup_map = self.patch_type.build_map(self.content)
        self._annotated = self.patch_type.build_annotation(self.content, self._lookup_map)

    async def validate_content(self) -> str | None:
        """Validate the object against the validation schema or condition."""

        if schema := self.validation_schema:
            try:
                schema.model_validate(self.content)
            except ValidationError as e:
                return str(e)

        if function := self.validation_condition:
            if inspect.iscoroutinefunction(function):
                return await function(self.content)
            else:
                return cast(Optional[str], function(self.content))
            
        return None


    @model_validator(mode="after")
    def validate_target_attribute(cls, v):
        """
        Validates that if target_attribute is provided, it exists as an attribute of target_object.
        """
        if v.content_attribute is not None:
            if not hasattr(v.object, v.content_attribute):
                raise ValueError(
                    f"object does not have attribute '{v.content_attribute}'"
                )
        return v
    
    @model_validator(mode="after")
    def validate_content_type(cls, v):
        """
        Validates that the content of the target object is a string.
        """
        if not v.validation_schema and not isinstance(v.content, str):
            raise ValueError("Validation schema must be provided for non-string target data")
        return v
    