from __future__ import annotations

from pydantic import BaseModel, Field, model_validator, PrivateAttr, ValidationInfo
from typing import List, Literal, Type, ClassVar, Any
from sortedcontainers import SortedDict
from ..base_patch import BasePatch, PatchPrompts, PatchBundle
from .prompts import STR_ANNOTATION_TEMPLATE, STR_PATCH_SYNTAX, ANNOTATION_PLACEHOLDER

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from llm_patch_driver.patch_target.target import PatchTarget

string_prompts = PatchPrompts(
    syntax=STR_PATCH_SYNTAX,
    annotation_template=STR_ANNOTATION_TEMPLATE,
    annotation_placeholder=ANNOTATION_PLACEHOLDER,
    modify_tool_doc="",
    reset_tool_doc="",
    request_tool_doc="",
)

class ReplaceOp(BaseModel):
    """Pattern substitution operation (no tids here)."""

    type: Literal["replace"] = "replace"
    pattern: str
    replacement: str

class DeleteOp(BaseModel):
    """Deletion operation - remove the supplied tids."""

    type: Literal["delete"] = "delete"

class InsertAfterOp(BaseModel):
    """Insert a new line after the line of *last tid*."""

    type: Literal["insert_after"] = "insert_after"
    text: str

class StrPatch(BasePatch):
    """A generic patch holding *where* (``tids``) and *what* (``operation``)."""

    tids: List[str] = Field(..., description="Sentence identifiers in '<line>_<sent>' form")
    operation: ReplaceOp | DeleteOp | InsertAfterOp

    prompts: ClassVar[PatchPrompts] = string_prompts

    # Internal cache of parsed tids for fast access during apply phase
    _parsed_tids: List[tuple[int, int]] = PrivateAttr()

    # Module-level cache for spaCy pipeline, scoped to this class
    _NLP: ClassVar[Any] = None

    @classmethod
    def _get_nlp(cls):
        """Return a cached spaCy pipeline, importing spaCy lazily.

        Loads `en_core_web_sm` if available, otherwise uses a blank English pipeline
        with the sentencizer. This avoids importing spaCy at module import time.
        """
        if cls._NLP is not None:
            return cls._NLP
        import spacy as _spacy
        try:
            cls._NLP = _spacy.load("en_core_web_sm")
        except OSError:
            cls._NLP = _spacy.blank("en")
            cls._NLP.add_pipe("sentencizer")
        return cls._NLP

    @classmethod
    def get_bundle_schema(cls) -> Type[PatchBundle]:
       
        class StrPatchBundle(PatchBundle):
            patches: List[StrPatch]

            __doc__ = f"Patch bundle. Syntax: {cls.prompts.syntax}"

            def model_post_init(self, __context):
                """Sort patches to keep coordinate validity: replacements first, then deletes, then inserts."""
                
                priority = {
                    "replace": 0,
                    "delete": 1,
                    "insert_after": 2,
                }

                def _anchor_line(patch: StrPatch) -> int:
                    # Inserts anchor to the last tid's line; deletes/replaces anchor to the highest referenced line
                    if patch.operation.type == "insert_after":
                        anchor_tid = patch.tids[-1]
                        return int(anchor_tid.split("_")[0])
                    return max(int(t.split("_")[0]) for t in patch.tids)

                # Sort patches to keep coordinate validity: replacements first, then deletes, then inserts.
                sorted_patches = sorted(
                    self.patches,
                    key=lambda p: (priority.get(p.operation.type, 99), -_anchor_line(p)),
                )
                self.patches = sorted_patches

        return StrPatchBundle

    def apply_patch(self, patch_target: 'PatchTarget') -> None:
        match self.operation:
            # -- replace -------------------------------------------------- #
            case ReplaceOp(pattern=pat, replacement=repl):
                for line, sent in self._parsed_tids:
                    segment: str = patch_target._lookup_map[line][sent]
                    patch_target._lookup_map[line][sent] = segment.replace(pat, repl)

            # -- delete --------------------------------------------------- #
            case DeleteOp():
                for line, sent in sorted(self._parsed_tids, key=lambda x: (x[0], x[1]), reverse=True):
                    line_map = patch_target._lookup_map[line]
                    del line_map[sent]
                    for sid in sorted([k for k in line_map if k > sent]):
                        line_map[sid - 1] = line_map.pop(sid)

                    if not line_map:
                        del patch_target._lookup_map[line]
                        for idx in range(line + 1, max(patch_target._lookup_map.keys(), default=line) + 1):
                            if idx in patch_target._lookup_map:
                                patch_target._lookup_map[idx - 1] = patch_target._lookup_map.pop(idx)

            # -- insert after ------------------------------------------- #
            case InsertAfterOp(text=text):
                anchor_line, _ = self._parsed_tids[-1]

                max_line = max(patch_target._lookup_map) if patch_target._lookup_map else 0
                for idx in range(max_line, anchor_line, -1):
                    patch_target._lookup_map[idx + 1] = patch_target._lookup_map[idx]

                new_line_id = anchor_line + 1
                nlp = self._get_nlp()
                doc = nlp(text)
                sents = [s.text for s in doc.sents] or [text]
                patch_target._lookup_map[new_line_id] = SortedDict({sid: s for sid, s in enumerate(sents, start=1)})

    @classmethod
    def build_map(cls,text: str) -> SortedDict:
        """Build a sentence map from a text.
        
        Sentence map is a lookup table that allows to quickly find a sentence or line by its id.
        """

        sent_map: SortedDict = SortedDict()
        lines = text.splitlines()
        nlp = cls._get_nlp()
        for line_idx, doc in enumerate(nlp.pipe(lines), start=1):
            line_sents: List[str] = [s.text_with_ws for s in doc.sents] or [lines[line_idx - 1]]
            sent_map[line_idx] = SortedDict({sid: s for sid, s in enumerate(line_sents, start=1)})

        return sent_map
    
    @classmethod
    def build_annotation(cls, data: str, map: SortedDict) -> str:
        """Assemble an annotated text from a sentence map.

        Used for LLM prompts to help LLMs modify the text.
        """
        annotated_parts: List[str] = []
        for line_id, line_map in map.items(): 
            for sent_id, sent in line_map.items():
                display_sentence = sent.rstrip()
                annotated_parts.append(f"<tid={line_id}_{sent_id}>{display_sentence}</tid>")

        return "\n".join(annotated_parts)
    
    @classmethod
    def content_from_map(cls, original_data: str, map: SortedDict) -> str:
        """Re-assemble a sentence map back into text.
        
        This is the inverse operation of build_map.
        """

        lines: List[str] = []
        for line_id, line_map in map.items():  
            sents = [line_map[sid] for sid in line_map]      
            lines.append("".join(sents))
            
        return "\n".join(lines)

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
    
    @model_validator(mode="after")
    def _check_ids(self, info: ValidationInfo):
        if isinstance(info.context, dict):
            id_map: dict = info.context.get("id_content_map", {})
            for line, sent in self._parsed_tids:
                if line not in id_map:
                    raise ValueError(f"Line {line} does not exist")
                if sent not in id_map[line]:
                    raise ValueError(f"Sentence {sent} does not exist in line {line}")

        return self

    