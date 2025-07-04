from __future__ import annotations

from typing import Any, Dict, List, Literal, Union, Optional

from pydantic import BaseModel, Field, ConfigDict, StrictBool, StrictFloat, StrictInt, model_validator

_JSON_PRIM_TYPES = Union[str, StrictInt, StrictBool, StrictFloat, None]
_JSON_TYPES = Union[_JSON_PRIM_TYPES, List[_JSON_PRIM_TYPES], Dict[str, _JSON_PRIM_TYPES]]

class JsonPatch(BaseModel):
    """A JSON Patch document represents an operation to be performed on a JSON document.

    Note that the op and path are ALWAYS required. Value is required for ALL operations except 'remove'.
    """

    op: Literal["add", "remove", "replace"] = Field(
        ...,
        description="The operation to be performed. Must be one of 'add', 'remove', 'replace'.",
    )
    a_id: int = Field(
        ...,
        description="The id of the key to be operated on"
    )
    i_id: Optional[int] = Field(
        None,
        description="The index of the item inside the array to be operated on.",
    )
    value: Union[_JSON_TYPES, List[_JSON_TYPES], Dict[str, _JSON_TYPES]] | None = Field(
        ...,
        description=(
            "The value to be used within the operation. REQUIRED for 'add', 'replace', "
            "and 'test' operations. Pay close attention to the json schema to ensure "
            "patched document will be valid."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"op": "replace", "path": "/path/to/my_array/1", "value": "the newer value to be patched"},
                {"op": "replace", "path": "/path/to/broken_object", "value": {"new": "object"}},
                {"op": "add", "path": "/path/to/my_array/-", "value": ["some", "values"]},
                {"op": "add", "path": "/path/to/my_array/-", "value": ["newer"]},
                {"op": "remove", "path": "/path/to/my_array/1"},
            ]
        }
    )

    @model_validator(mode="after")
    def _check_ops(self, v):
        """Check that the anchor and index ids are valid."""

        if self.op in ["add", "replace"] and self.value is None:
            raise ValueError("Value is required for 'add' and 'replace' operations.")
        
        if self.op == "remove" and self.value is not None:
            raise ValueError("Value is not allowed for 'remove' operations.")
        
        if self.op == "replace" and self.i_id is not None:
            raise ValueError("Index id is not allowed for 'replace' operations.")
        
        return v
        