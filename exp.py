from pydantic import BaseModel, Field, model_validator, ValidationInfo

class Test(BaseModel):
    """This is the test model."""
    name: str = Field(description="The name of the test.")
    age: int = Field(description="The age of the test.")

print(Test.__doc__)

test = Test(name="John", age=20)

print(test.__doc__)

Test.__doc__ = "This is kek."


print(test.__doc__)
print(Test.__doc__)