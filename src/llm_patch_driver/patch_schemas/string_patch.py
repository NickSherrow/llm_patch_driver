from pydantic import BaseModel, Field, model_validator, PrivateAttr
from typing import List, Literal
from sortedcontainers import SortedDict
from .base_patch import BasePatch

class ReplaceOp(BaseModel):
    """Pattern substitution operation (no tids here)."""

    type: Literal["replace"] = "replace"
    pattern: str
    replacement: str

class DeleteOp(BaseModel):
    """Deletion operation – remove the supplied tids."""

    type: Literal["delete"] = "delete"

class InsertAfterOp(BaseModel):
    """Insert a new line after the line of *last tid*."""

    type: Literal["insert_after"] = "insert_after"
    text: str

class StrPatch(BasePatch):
    """A generic patch holding *where* (``tids``) and *what* (``operation``)."""

    tids: List[str] = Field(..., description="Sentence identifiers in '<line>_<sent>' form")
    operation: ReplaceOp | DeleteOp | InsertAfterOp

    # Internal cache of parsed tids for fast access during apply phase
    _parsed_tids: List[tuple[int, int]] = PrivateAttr()

    # ------------------------------------------------------------------ #
    # Post-init parsing & validation of tids string → int tuples
    # ------------------------------------------------------------------ #

    def validate_map(self, map: SortedDict):
        """Validate the map against the patch."""

        for line, sent in self._parsed_tids:
            if line not in map:
                raise ValueError(f"Line {line} does not exist")
            
            if sent not in map[line]:
                raise ValueError(f"Sentence {sent} does not exist in line {line}")
    
    @classmethod        
    def bundle_builder(cls, patches: List['StrPatch']) -> List['StrPatch']:
        """Sort patches to keep coordinate validity: replacements first, then deletes, then inserts."""

        priority = {
            "replace": 0,
            "delete": 1,
            "insert_after": 2,
        }

        def _anchor_line(patch: 'StrPatch') -> int:
            anchor_tid = patch.tids[-1] if patch.operation.type == "insert_after" else patch.tids[0]
            return int(anchor_tid.split("_")[0])

        # Sort patches to keep coordinate validity: replacements first, then deletes, then inserts.
        sorted_patches = sorted(
            patches,
            key=lambda p: (priority.get(p.operation.type, 99), -_anchor_line(p)),
        )
        return sorted_patches

    @model_validator(mode="after")
    def _parse_tids(cls, v):  # type: ignore[cls-parameter-name]
        parsed: List[tuple[int, int]] = []

        if not v.tids:
            raise ValueError("Patch must contain at least one tid")
        
        for tid in v.tids:
            try:
                l_str, s_str = tid.split("_")
                parsed.append((int(l_str), int(s_str)))

            except Exception:
                raise ValueError(f"Invalid tid format '{tid}'. Expected '<line>_<sentence>'.")

        v._parsed_tids = parsed

        return v