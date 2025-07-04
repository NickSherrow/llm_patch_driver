from pydantic import BaseModel
from typing import Literal

class LibConfig(BaseModel):
    api_type: Literal["responses", "chat_completion", "custom"] = "chat_completion"

config = LibConfig()