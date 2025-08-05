from typing import Any, List, Optional
from sortedcontainers import SortedDict

from .sentencizer import NLP

def build_map(text: str) -> SortedDict:
    """Build a sentence map from a text.
    
    Sentence map is a lookup table that allows to quickly find a sentence or line by its id.
    """

    sent_map: SortedDict = SortedDict()
    lines = text.splitlines()
    for line_idx, doc in enumerate(NLP.pipe(lines), start=1):
        # Keep sentences exactly as they appear in the original text.
        line_sents: List[str] = [s.text for s in doc.sents] or [lines[line_idx - 1]]
        sent_map[line_idx] = SortedDict({sid: s for sid, s in enumerate(line_sents, start=1)})

    return sent_map

def map_to_original_text(map: SortedDict) -> str:
    """Re-assemble a sentence map back into text.
    
    This is the inverse operation of build_map.
    """

    lines: List[str] = []
    for line_id, line_map in map.items():  
        sents = [line_map[sid] for sid in line_map]      
        lines.append("".join(sents))
        
    return "\n".join(lines)

def map_to_annotated_text(sentence_map: SortedDict) -> str:
    """Assemble an annotated text from a sentence map.
    
    Used for LLM prompts to help LLMs modify the text.
    """

    annotated_parts: List[str] = []
    for line_id, line_map in sentence_map.items(): 
        for sent_id, sent in line_map.items():            
            annotated_parts.append(f"<tid={line_id}_{sent_id}>{sent}</tid>")

    return "\n".join(annotated_parts)

def build_json_annotation_and_map(
    data: Any,
    _attr_idx_start: int = 1,
    _item_idx_start: int = 1,
    _path: str = "",
    _attr_map: Optional[SortedDict] = None,
) -> tuple[Any, SortedDict]:
    """Build an annotated version of a JSON object, and it's id map.
    
    Annotated version of the JSON has id tags that help LLMs navigate the JSON.
    Map is a lookup table that allows to quickly find a key or item by its id.
    Used for LLM prompts to help LLMs modify the JSON.
    """

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
        # Use plain dict for the annotated representation. Insertion order is
        # preserved in Python 3.7+, so we no longer need SortedDict here.
        annotated_dict: dict[Any, Any] = {}
        attr_idx = _attr_idx_start
        for key, value in data.items():
            annotated_key = f"<a={attr_idx} k={key}>"
            _attr_map[attr_idx] = _json_pointer(_path, key)
            annotated_value, _ = build_json_annotation_and_map(
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
                annotated_element, _ = build_json_annotation_and_map(
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
