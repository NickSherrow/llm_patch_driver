from pydantic import BaseModel, Field, model_validator, PrivateAttr
from typing import List, Literal

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

class StrPatch(BaseModel):
    """A generic patch holding *where* (``tids``) and *what* (``operation``)."""

    tids: List[str] = Field(..., description="Sentence identifiers in '<line>_<sent>' form")
    operation: ReplaceOp | DeleteOp | InsertAfterOp

    # Internal cache of parsed tids for fast access during apply phase
    _parsed_tids: List[tuple[int, int]] = PrivateAttr()

    # ------------------------------------------------------------------ #
    # Post-init parsing & validation of tids string → int tuples
    # ------------------------------------------------------------------ #
    @model_validator(mode="after")
    def _parse_tids(cls, v):  # type: ignore[cls-parameter-name]
        parsed: List[tuple[int, int]] = []
        for tid in v.tids:
            try:
                l_str, s_str = tid.split("_")
                parsed.append((int(l_str), int(s_str)))
            except Exception:
                raise ValueError(f"Invalid tid format '{tid}'. Expected '<line>_<sentence>'.")

        v._parsed_tids = parsed
        return v