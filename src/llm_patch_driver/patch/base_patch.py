from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel
from abc import ABC, abstractmethod
from sortedcontainers import SortedDict
from typing import List, Type, Any, Callable, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from llm_patch_driver.patch_target.target import PatchTarget

@dataclass
class PatchPrompts: #TODO: check that provided string templates have all required variables
    """All patch types must have syntax and usage specific templates for prompts."""
    syntax: str
    annotation_template: str
    annotation_placeholder: str
    modify_tool_doc: str
    reset_tool_doc: str
    request_tool_doc: str

class PatchBundle(BaseModel, ABC):
    """A bundle of patches."""
    patches: List[BasePatch]

class BasePatch(BaseModel, ABC):
    """Base class for all patch types."""
    prompts: PatchPrompts

    @classmethod
    @abstractmethod
    def get_bundle_schema(cls) -> Type[PatchBundle]:
        """Build a bundle schema."""

    @abstractmethod
    def apply_patch(self, patch_target: PatchTarget) -> None:
        """Apply the patch to the patch target."""

    @classmethod
    @abstractmethod
    def build_map(cls, data: Any) -> SortedDict:
        """Build a map from the data."""

    @classmethod
    @abstractmethod
    def build_annotation(cls, data: Any, map: SortedDict) -> str:
        """Build an annotation from the map."""

    @classmethod
    @abstractmethod
    def content_from_map(cls, original_data: Any, map: SortedDict) -> Any:
        """Build a content from the map."""