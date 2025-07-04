from typing import Generic, Type, Callable, Optional, Coroutine, Any, TypeVar, List, Dict
from pydantic import BaseModel, model_validator, ValidationError
from sortedcontainers import SortedDict
import inspect
import spacy

T = TypeVar("T")

# --------------------------------------------------------------------- #
# DATA WRAPPER CLASS
# --------------------------------------------------------------------- #

class PatchTarget(BaseModel, Generic[T]):
    """Container for the object to be patched."""

    object: T
    content_attribute: str | None = None
    validation_condition: Callable[[T], Optional[str] | Coroutine[Any, Any, Optional[str]]] | None = None
    validation_schema: Type[BaseModel] | None = None

    @property
    def content(self) -> Any:
        if self.content_attribute is None:
            return self.object
        else:
            return getattr(self.object, self.content_attribute)
        
    @content.setter
    def content(self, value: Any) -> None:
        if self.content_attribute is None:
            self.object = value
        else:
            setattr(self.object, self.content_attribute, value)

    async def validate_content(self) -> str | Coroutine[Any, Any, str | None] | None:
        """Validate the object against the validation schema or condition."""

        if schema := self.validation_schema:
            try:
                schema.model_validate(self.object)
            except ValidationError as e:
                return str(e)

        if function := self.validation_condition:
            if inspect.iscoroutinefunction(function):
                return await function(self.object)
            else:
                return function(self.object)
            
        return None


    @model_validator(mode="after")
    def validate_target_attribute(cls, v):
        """
        Validates that if target_attribute is provided, it exists as an attribute of target_object.
        """
        if v.content_attribute is not None:
            if not hasattr(v.object, v.content_attribute):
                raise ValueError(
                    f"object does not have attribute '{v.content_attribute}'"
                )
        return v
    
    @model_validator(mode="after")
    def validate_content_type(cls, v):
        """
        Validates that the content of the target object is a string.
        """
        if not v.validation_schema and not isinstance(v.content, str):
            raise ValueError("Validation schema must be provided for non-string target data")
        return v
    