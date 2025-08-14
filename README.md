# LLM Patch Driver

This library lets LLMs modify existing data objects (both structured and unstructured). It can generate and apply a single patch, or start the patching loop to fix complex validation issues.

This library is framework/client agnostic and allows you to add your own patch types and validation logic.

**Useful when**:
1. You want to modify existing big document and you want to control what exactly should be changed.
2. You want LLM to create an object from a huge Pydantic schema with recursions and custom validation (i.e., generate a valid DAG with 100+ nodes).
3. Your prompt has too many instructions and conditions that must be met.
4. Your desired response from LLM is too big for the output window.

**Installation**:
```bash
pip install llm-patch-driver
```

Or with uv:
```bash
uv add llm-patch-driver
```

**Applications**:
1. Creating and updating graphs.
2. Generating and updating long documents.
3. Modifying codebases.
4. Data extraction with complex schemas.

## Quick Example

**Set up the patch target and driver.**

```python
import openai
from llm_patch_driver import PatchTarget, PatchDriver, StrPatch

client = openai.OpenAI()

# Create a patch target for your content
target = PatchTarget(
    object="The quick brown fox jumps over the lazy dog.",
    patch_type=StrPatch
)

# Set up the driver with your LLM client
driver = PatchDriver(
    target_object=target,
    create_method=client.chat.completions.create,
    parse_method=client.beta.chat.completions.parse,
    model_args={'model': 'gpt-4o-mini'},
)
```

**Option 1: Request a patch using a query and apply it to the target**

```python
patch_bundle = await driver.request_patch_bundle(
    query="Replace 'brown' with 'red' and 'lazy' with 'sleepy'"
)
await target.apply_patches(patch_bundle.patches)

print(target.object)  # "The quick red fox jumps over the sleepy dog."
```

**Option 2: Provide a validation condition and run the patching loop to ensure the required number of words is met**

```python
def word_count_validator(text: str) -> str | None:
    word_count = len(text.split())
    if word_count < 55:
        return f"The poem must be at least 55 words, currently has {word_count} words"
    return None

target.validation_condition = word_count_validator

await driver.run_patching_loop(messages)

print(target.object)  # "The quick red fox jumps over the sleepy dog. Then, with nimble paws and a glint in its eye, the fox danced through fields of gold, beneath a sky painted with dawn's first light. Birds sang, dew sparkled, and the world awoke as the fox's journey continued, weaving a story exactly fifty-five words long. Joyful."
```

## Examples

For comprehensive examples showing real-world usage:

- **String Patching**: See [tests/end_to_end/test_string.py](tests/end_to_end/test_string.py) for examples of text modification, validation, and complex string operations
- **JSON Patching**: See [tests/end_to_end/test_json.py](tests/end_to_end/test_json.py) for examples of structured data modification with Pydantic schemas and complex object validation

## Components

### Overview

The library includes the following components:
* PatchTarget (wrapper for data you want to modify)
* PatchDriver (handles LLM calls and generates patches)
* BaseApiAdapter (formats core LLM objects for your LLM client)
* BasePatch (stores both patch data and application methods)

### PatchTarget

**Description:**
PatchTarget is a wrapper around data objects that need to be modified. It acts as a smart container that holds your target content, validation logic, and patch application behavior. The component automatically creates backup copies, generates annotations for LLM understanding, and maintains lookup maps for efficient patching.

**Key responsibilities**:
- Validates content against Pydantic schemas or custom validation functions  
- Annotates content with metadata to help LLMs understand structure
- Stores backup copies for reset functionality
- Applies patches to the wrapped object in-place
- Tracks validation errors and debugging states

**Examples:**
```python
from llm_patch_driver import PatchTarget, StrPatch, JsonPatch
from pydantic import BaseModel

# String patching with custom validation
def word_count_validator(text: str) -> str | None:
    if len(text.split()) != 500:
        return f"Text must be exactly 500 words, got {len(text.split())}"
    return None

string_target = PatchTarget(
    object="Your document content here...",
    validation_condition=word_count_validator,
    patch_type=StrPatch
)

# JSON patching with Pydantic schema validation
class Company(BaseModel):
    name: str
    employees: list[dict]

json_target = PatchTarget(
    object={"name": "Acme Corp", "employees": []},
    validation_schema=Company,
    patch_type=JsonPatch
)

# Nested object patching (content lives in an attribute)
@dataclass
class Document:
    content: str
    metadata: dict

doc_target = PatchTarget(
    object=Document(content="text to patch", metadata={}),
    content_attribute="content",  # Patch the 'content' attribute
    patch_type=StrPatch
)
```

### PatchDriver

**Description:**
PatchDriver is the orchestration engine that coordinates the entire patching process. It handles LLM communication, executes tool calls, and runs the iterative patching loop until validation succeeds or maximum cycles are reached. The driver is LLM-provider agnostic through the adapter pattern.

**Key responsibilities**:
- Executes LLM calls using provided create/parse methods
- Manages the autonomous patching loop with error handling
- Supports both single patch generation and iterative fixing
- Integrates with tool systems for LLM function calling
- Provides debugging states and error tracking

**Examples:**
```python
from llm_patch_driver import PatchDriver
from llm_patch_driver.llm import OpenAIChatCompletions
import openai

# OpenAI setup
client = openai.OpenAI()
driver = PatchDriver(
    target_object=your_patch_target,
    create_method=client.chat.completions.create,
    parse_method=client.beta.chat.completions.parse,
    model_args={'model': 'gpt-4o-mini'},
    api_adapter=OpenAIChatCompletions(),
    max_cycles=25
)

# Generate a single patch from a query
patch_bundle = await driver.request_patch_bundle(
    query="Fix the spelling errors in the document",
    context="This is a legal contract draft"
)

# Run autonomous patching loop until valid
messages = [{"role": "user", "content": "Generate a valid company structure..."}]
await driver.run_patching_loop(messages)

# Google Gemini setup
from google import genai
from llm_patch_driver.llm import GoogleGenAiAdapter

client = genai.Client(vertexai=True, project="your-project")
driver = PatchDriver(
    target_object=your_patch_target,
    create_method=client.models.generate_content,
    parse_method=client.models.generate_content,
    model_args={'model': 'gemini-2.5-pro'},
    api_adapter=GoogleGenAiAdapter()
)
```

### BaseApiAdapter

**Description:**
BaseApiAdapter provides a standardized interface for integrating different LLM providers. It abstracts away provider-specific API formats, message structures, and tool schemas, allowing PatchDriver to work seamlessly with OpenAI, Google, or any other LLM provider.

*Prebuilt adapters: OpenAIChatCompletions, OpenAIResponses, GoogleGenAiAdapter*

**Key responsibilities**:
- Converts standardized inputs into provider-specific API call parameters
- Parses provider responses back into standardized internal Message objects
- Formats tool schemas according to each provider's function calling conventions
- Handles provider-specific message formatting (roles, content structure, etc.)

**Examples:**
```python
from llm_patch_driver.llm import OpenAIChatCompletions, GoogleGenAiAdapter
from llm_patch_driver.llm.schemas import Message

# OpenAI adapter usage
openai_adapter = OpenAIChatCompletions()

# Format messages for OpenAI API
api_params = openai_adapter.format_llm_call_input(
    messages=[Message(role="user", content="Fix this JSON")],
    tools=[tool_schema_dict],
    system_prompt="You are a helpful assistant"
)
# Returns: {"messages": [...], "tools": [...], "model": "gpt-4"}

# Parse OpenAI response back to standard format
response = openai_adapter.parse_llm_output(openai_raw_response)
# Returns: Message(role="assistant", content="...", tool_calls=[...])

# Google Gemini adapter usage  
google_adapter = GoogleGenAiAdapter()

# Same interface, different provider
api_params = google_adapter.format_llm_call_input(
    messages=[Message(role="user", content="Fix this JSON")],
    schema=YourPydanticModel
)
# Returns: {"contents": [...], "generation_config": {...}}

# Custom adapter implementation
class CustomAdapter(BaseApiAdapter):
    def format_llm_call_input(self, messages, tools=None, schema=None, system_prompt=None):
        # Convert to your provider's format
        return {"your_provider_format": "..."}
    
    def parse_llm_output(self, raw_response):
        # Convert back to Message object
        return Message(role="assistant", content="...")
```

### BasePatch

**Description:**
BasePatch is the abstract base class that defines how modifications are represented and applied to content. Concrete implementations handle different data types (strings, JSON) with their own patch formats and application logic. Each patch type includes specialized prompts and annotation systems optimized for LLM understanding.

*Prebuilt patch types: StrPatch, JsonPatch*

**Key responsibilities**:
- Defines patch data structure and validation rules
- Implements content-specific patch application logic
- Builds lookup maps for efficient content navigation

**Examples:**
```python
# String patches with sentence-level targeting
from llm_patch_driver.patch.string import StrPatch, ReplaceOp, DeleteOp, InsertAfterOp

# Replace operation targeting specific sentences
string_patch = StrPatch(
    tids=["1_2", "1_3"],  # Line 1, sentences 2 and 3
    operation=ReplaceOp(
        pattern="old text",
        replacement="new text"
    )
)

# Delete specific sentences
delete_patch = StrPatch(
    tids=["2_1"],  # Line 2, sentence 1
    operation=DeleteOp()
)

# Insert new content after a sentence
insert_patch = StrPatch(
    tids=["3_4"],  # After line 3, sentence 4
    operation=InsertAfterOp(text="This is new content to insert.")
)

# JSON patches using JSONPath-style operations
from llm_patch_driver.patch.json import JsonPatch

# Replace a JSON value
json_patch = JsonPatch(
    op="replace",
    a_id=5,  # Attribute ID from annotation map
    value="new value"
)

# Add to JSON array
array_patch = JsonPatch(
    op="add", 
    a_id=3,
    i_id=2,  # Index within array
    value={"new": "object"}
)

# Remove JSON property
remove_patch = JsonPatch(
    op="remove",
    a_id=7
)

# Custom patch implementation
class CustomPatch(BasePatch):
    @classmethod
    def get_bundle_schema(cls):
        # Define how patches are bundled together
        pass
        
    def apply_patch(self, patch_target):
        # Implement your patch application logic
        pass
        
    @classmethod  
    def build_map(cls, data):
        # Create lookup map for content navigation
        pass
        
    @classmethod
    def build_annotation(cls, data, map):
        # Generate annotated version for LLM prompts
        pass
```

## Roadmap

1. Replace spaCy sentencizer with a lightweight alternative
2. Optimize content-map-annotation loop performance
3. Add robust fallback handling for corrupted LLM patch responses
4. Implement improved validation interface and error reporting

## Contributing

Contributions are welcome! We're particularly interested in:
- New LLM provider adapters (ApiAdapters)
- Additional patch types for different data formats
- Performance optimizations and bug fixes
- Documentation improvements

Please feel free to open issues for feature requests or bug reports, and submit pull requests for any enhancements.
