from .config import config                              # stays the same

from .patch_target.target        import PatchTarget
from .driver.driver              import PatchDriver
from .patch.json.json_patch   import JsonPatch
from .patch.string.string_patch import StrPatch

__all__ = [
    "config",
    "PatchTarget",
    "PatchDriver",
    "JsonPatch",
    "StrPatch",
]