from __future__ import annotations

from pydantic import BaseModel
from abc import ABC, abstractmethod
from sortedcontainers import SortedDict
from typing import List

class PatchBundle(BaseModel):
    """A bundle of patches."""

    patches: List[BasePatch]

class BasePatch(BaseModel, ABC):
    """Base class for all patches."""

    @abstractmethod
    def validate_map(self, map: SortedDict) -> None:
        """Validate the map against the patch."""

    @classmethod
    @abstractmethod
    def bundle_builder(cls, patches: List['BasePatch']) -> List['BasePatch']:
        """Build a bundle of patches."""
