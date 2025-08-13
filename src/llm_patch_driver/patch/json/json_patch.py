from __future__ import annotations

from typing import Any, Dict, List, Literal, Union, Optional, Type, ClassVar
from pydantic import BaseModel, Field, ConfigDict, StrictBool, StrictFloat, StrictInt, model_validator, ValidationInfo
from sortedcontainers import SortedDict
import jsonpatch
import json

from ..base_patch import BasePatch, PatchBundle, PatchPrompts
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_patch_driver.patch_target.target import PatchTarget
from .prompts import JSON_ANNOTATION_TEMPLATE, JSON_PATCH_SYNTAX, ANNOTATION_PLACEHOLDER

_JSON_PRIM_TYPES = Union[str, StrictInt, StrictBool, StrictFloat, None]
_JSON_TYPES = Union[_JSON_PRIM_TYPES, List[_JSON_PRIM_TYPES], Dict[str, _JSON_PRIM_TYPES]]

json_prompts = PatchPrompts(
    syntax=JSON_PATCH_SYNTAX,
    annotation_template=JSON_ANNOTATION_TEMPLATE,
    annotation_placeholder=ANNOTATION_PLACEHOLDER,
    modify_tool_doc="",
    reset_tool_doc="",
    request_tool_doc="",
)

class JsonPatch(BasePatch):
    """A JSON Patch document represents an operation to be performed on a JSON document.

    Note that the op and path are ALWAYS required. Value is required for ALL operations except 'remove'.
    """

    op: Literal["add", "remove", "replace"] = Field(
        ...,
        description="The operation to be performed.",
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

    prompts: ClassVar[PatchPrompts] = json_prompts

    @classmethod
    def get_bundle_schema(cls) -> Type[PatchBundle]:
        class JsonPatchBundle(PatchBundle):
            patches: List[JsonPatch]

            __doc__ = f"Patch bundle. Syntax: {cls.prompts.syntax}"

        return JsonPatchBundle

    def apply_patch(self, patch_target: 'PatchTarget') -> None:
        path = patch_target._lookup_map[self.a_id]

        if self.i_id is not None:
            path = f"{path}/{self.i_id - 1}"  

        match self.op:
            case "replace":
                op_dict = {"op": "replace", "path": path, "value": self.value}

            case "add":
                op_dict = {"op": "add", "path": path, "value": self.value}

            case "remove":
                op_dict = {"op": "remove", "path": path}
            
        patch_obj = jsonpatch.JsonPatch([op_dict])
        patch_obj.apply(patch_target.content, in_place=True)

    @classmethod
    def build_map(
        cls,
        data: Any,
        _attr_idx_start: int = 1,
        _path: str = "",
        _attr_map: Optional[SortedDict] = None,
    ) -> SortedDict:
        """Build an id-to-jsonpath map for a JSON object.
        
        Map is a lookup table that allows to quickly find a key or item by its id.
        Used for LLM prompts to help LLMs modify the JSON.
        """
        
        if _attr_map is None:
            _attr_map = SortedDict()

        # -- dict ----------------------------------------------------------- #
        if isinstance(data, dict):
            attr_idx = _attr_idx_start
            for key, value in data.items():
                _attr_map[attr_idx] = cls._json_pointer(_path, key)
                cls.build_map(
                    value,
                    _attr_idx_start=attr_idx + 1,
                    _path=cls._json_pointer(_path, key),
                    _attr_map=_attr_map,
                )
                attr_idx = max(_attr_map.keys()) + 1

        # -- list ----------------------------------------------------------- #
        elif isinstance(data, list):
            for item_idx, element in enumerate(data):
                if isinstance(element, (dict, list)):
                    next_free_id = max(_attr_map.keys()) + 1 if _attr_map else _attr_idx_start
                    cls.build_map(
                        element,
                        _attr_idx_start=next_free_id,
                        _path=cls._json_pointer(_path, item_idx),
                        _attr_map=_attr_map,
                    )

        return _attr_map
    
    @classmethod
    def build_annotation(
        cls,
        data: Any, 
        attr_map: SortedDict,
        _item_idx_start: int = 1,
        _path: str = "",
    ) -> Any:
        """Build an annotated version of a JSON object using a pre-built map.
        
        Annotated version of the JSON has id tags that help LLMs navigate the JSON.
        Uses the attr_map to find the correct attribute IDs for each path.
        """

        # Create reverse lookup: path -> attr_id
        path_to_id = {path: attr_id for attr_id, path in attr_map.items()}

        # -- dict ----------------------------------------------------------- #
        if isinstance(data, dict):
            annotated_dict: dict[Any, Any] = {}
            for key, value in data.items():
                key_path = cls._json_pointer(_path, key)
                attr_id = path_to_id[key_path]
                annotated_key = f"<a={attr_id} k={key}>"
                
                annotated_value = cls.build_annotation(
                    value,
                    attr_map,
                    _item_idx_start=1,
                    _path=key_path,
                )
                    
                annotated_dict[annotated_key] = annotated_value

            if _path == "":
                return json.dumps(annotated_dict, indent=4, ensure_ascii=False)
            return annotated_dict

        # -- list ----------------------------------------------------------- #
        elif isinstance(data, list):
            annotated_list: List[Any] = []
            item_idx = _item_idx_start
            for element in data:
                if isinstance(element, (dict, list)):      
                    annotated_element = cls.build_annotation(
                        element,
                        attr_map,
                        _item_idx_start=1,
                        _path=cls._json_pointer(_path, item_idx - 1),
                    )
                else:
                    annotated_element = f"<i={item_idx} v={element}>"

                annotated_list.append(annotated_element)
                item_idx += 1

            if _path == "":
                return json.dumps(annotated_list, indent=4, ensure_ascii=False)
            return annotated_list

        if _path == "":
            return json.dumps(data, indent=4, ensure_ascii=False)
        return data
    
    @classmethod
    def content_from_map(cls, original_data: Any, map: SortedDict) -> Any:
        """Build a content from the map."""

        return original_data

    # @model_validator(mode="after")
    # def _check_ops(self):
    #     """Check that the anchor and index ids are valid."""

    #     if self.op in ["add", "replace"] and self.value is None:
    #         raise ValueError("Value is required for 'add' and 'replace' operations.")
        
    #     if self.op == "remove" and self.value is not None:
    #         raise ValueError("Value is not allowed for 'remove' operations.")
        
    #     if self.op == "replace" and self.i_id is not None:
    #         raise ValueError("Index id is not allowed for 'replace' operations.")
        
    #     return self
    
    @model_validator(mode="after")
    def _check_ids(self, info: ValidationInfo):

        if isinstance(info.context, dict):
            id_map: dict = info.context.get("id_content_map", {})

            if not self.a_id:
                raise ValueError("Patch must contain an attribute id")

            if self.a_id not in id_map:
                raise ValueError(f"Attribute {self.a_id} does not exist")

        return self
    
    @classmethod
    def _json_pointer(cls, parent: str, token: str | int) -> str:
        """Build a JSON Pointer by appending *token* to *parent*."""
        # Per RFC 6901 we need to escape '~' and '/' in reference tokens.
        if isinstance(token, str):
            token = token.replace('~', '~0').replace('/', '~1')
        return f"{parent}/{token}" if parent else f"/{token}"