# LLM patch generator

## TLDR: when working with long and complex documents (both structured and unstructured), allowing LLM to update the existing document with patches instead of generating the new document if an error is caught delivers much better results. This library introduces a very simple SDK to help developers introduce patch generation to their existing LLM apps.

## Components

### PatchTarget

Description: Wrap the document you want to modify into PatchTarget and add required Pydantic schemas and/or validation callables for validation. PatchDriver will keep looping until both schema and validation callable stop raising errors.

### PatchDriver

Description: core interface. Provide the PatchTarget and either start the autonomous fixing loop, or generate a patch with a specific query.

### LLMClientWrapper

Description: LLM patch generator is low-key model agnostic, so you should wrap the LLM client you use into LLMClientWrapper.

## Usage

### Generate graphs with complex relations by creating an BaseModel schema with the following validation:
- check parent-child ids for nested objects to make sure the nesting relations are correct
- check how many levels you want for different cases
- check that no duplicate nodes exist in the graph
- generate object using the schema
- if fails - start patch loop

### Generate legal contracts with strict reflection on each section/statement
- build a draft using structured output to determine the exact number of items
- compile validation logic during runtime for reflection
- generate the first version
- if fails - start patch loop
- let human review
- if human unhappy - generate patch

<FOR LLM CODING AGENTS>

desired behavior:

1. user wrap existing LLM client into LLMClientWrapper. Since different LLM providers and frameworks have different APIs, the wrapper was made to work in two ways: if API is compatible with OpenAI Chat Completions API or Responses API, then the user should just setup the right config. If they use something different they are allowed to provide a custome API map that would be used for aligning their API to what we use in this lib

2. wrapper handles the core interactions with an LLM: it makes sure that LLM receives messages and data in supportable way. We expect that the user would provide async functions for generating a structured and unstructured data, and if necessary, an API map.

3. after the user created the wrapper, they attach it to the PatchDriver.client. Now they could create new instances of the patchdriver for different parts of their pipeline. Planned usage: if their standard LLM returns a json that can't be parsed by the BaseModel schema without validation errors, or they have reflection LLM layer that returned some problems with the initial output, they wrap the output into PatchTarget and create an instance of PatchDriver with this PatchTarget

4. Now they could run patch loop by providing message history and error message so the patch driver will figure out the best way how to fix the object, or they could describe the modification to the driver and generate a patch and then apply it

5. All modifications happen in-place so they could just use the passed object as soon as the driver finished. Or they could use the driver to return the object to its original state

</FOR LLM CODING AGENTS>