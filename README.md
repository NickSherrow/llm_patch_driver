# LLM patch generator

## TLDR: when working with long and complex documents (both structured and unstructured), allowing LLM to update the existing document with patches instead of generating the new document if an error is caught delivers much better results. This library introduces a very simple SDK to help developers introduce patch generation to their existing LLM apps.

## Components

### PatchTarget

Description: Wrap the document you want to modify into PatchTarget and add required Pydantic schemas and/or validation callables for validation. PatchDriver will keep looping until both schema and validation callable stop raising errors.

### PatchDriver

Description: core interface. Provide the PatchTarget and either start the autonomous fixing loop, or generate a patch with a specific query.

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
