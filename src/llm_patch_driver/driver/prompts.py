REQUEST_PATCH_PROMPT = """
    You are a professional editor specialised in programmatic text refactoring. 
    Given an original text and a modification request, your task is to emit a JSON object 
    with patch operations that will transform the text so it satisfies the request.

    <best_practices>
        1. Think step-by-step. Identify what granular edit each patch should perform.
        2. Prefer provinig more specific patches.
        3. Avoid overlapping patches that modify the same span - this makes reasoning about the transformation easier.
        4. If several independent edits are required, include them all in the same JSON array.
    </best_practices>

    <modification_request>
        <guidelines>
            1. The <query> section explains *exactly* what must change. Do not introduce additional, unrequested modifications.
            2. The <context> section may contain auxiliary information that helps you locate the correct portion of the text. Use it, but do not treat it as text to be edited (unless explicitly stated).
            3. The <annotated_text> section is the text that must be modified. It was annotated with <tid> tags. Each tid is a unique identifier for a sentence in the text.

            <tid_annotation>
                'tid' tags help you modify the text. Each tid is a unique identifier for a sentence in the text.
                Use these unique identifiers to generate a patch that will modify the text. The final text will not have any annotations. 
                This is just a temporary view to help you modify the text.
            </tid_annotation>

        <query>
            {query}
        </query>

        <context>
            {context}
        </context>

        <annotated_text>
            {text}
        </annotated_text>
    </modification_request>
    """

PATCHING_LOOP_SYSTEM_PROMPT = """
<current_stage_context>
    Your response was not approved by the validation engine. You must fix your response.
    Below you will information about the error, guidelines how to fix it, and tools that you can use to fix the data.
</current_stage_context>

<goal>
    Your goal is to make the data pass the validation without error messages.
</goal>

<fixing_process>
    1. Below you will find a debugging state. It contains information about error, and annotated version of the data.
    2. You now have access to a set of tools. Each can modify the data in a specific way.
    3. Each time you modify the data, the validation pipeline will try to validate the data again.
    4. If the data is still not valid, you see the new debuggin state with the new error message, and updated annotated version of the data.
    5. Previous debugging states will be still available in the conversation to track your progress, but annotated state will be available only in the latest debugging state.
</fixing_process>

<guidelines>
    <core_instructions>
        1. First, analyze the validation error message. Figure out why it happened.
        2. Figure out how to meet the condition required by the validation error message. What exactly needs to be changed?
        3. Start fixing the data. Use the tools to fix the data.
        4. Keep doing that until the data passes the validation without error messages.
    </core_instructions>

    <tools>
        You have access to a set of tools. Each can modify the data through patches. You can:
        - Request a patch from the LLM if the modification is too complex for you to provide it yourself.
        - Provide a patch yourself if the modification is simple enough.
        - Reset the data to the original state if you want to start over.
    </tools>

    <patch_syntax>
        {patch_syntax}
    </patch_syntax>
</current_stage_guidelines>
"""

TRY_AGAIN_PROMPT = """
<current_stage_of_pipeline>
    The response was not approved by the pipeline. It needs to be fixed.
</current_stage_of_pipeline>
<negative_feedback>
    Your response is not correct. Below you'll find what exactly is wrong. Read the error description carefully and fix the response.
    <error_description>
        {error_description}
    </error_description>
</negative_feedback>
<instructions>
    1. Read the error description carefully.
    2. Generate the response again, but this time make sure that you fix the error.
    3. Important: you must generate the entire response again. Not just a fixed part of it.
</instructions>
"""

FIX_JSON_PROMPT = """
<error>
    The previous response was not approved by the pipeline. See the error description below. It needs to be fixed. Generate an RFC 6902 patch.
</error>

<handling_error>
    1. You generated a JSON object. It failed to pass the validation, and/or parsing.
    2. This JSON object could be fixed by applying a RFC 6902 patch.
    3. Your job is to return the patch.
    4. This patch will be applied automatically by patch_json function.
    5. Below you will see the error description, the current state of the object, and the schema that was used to validate the object.
</handling_error>

<current_state_of_the_object>
    {state_of_the_object}
</current_state_of_the_object>

<detected_problem>
    {error_description}
</detected_problem>

<schema_that_was_used_to_validate_the_object>
    {schema}
</schema_that_was_used_to_validate_the_object>
"""

CORRUPTED_PATCH_PROMPT = """
<error>
    The previous JSON patch was not approved by the pipeline. It needs to be fixed.
</error>

<handling_error>
    1. You generated a JSON patch. The application of the patch raised an error.
    2. Analyze the error description and return the new patch.
</handling_error>

<detected_problem>
    {detected_problem}
</detected_problem>
"""

ORIGINAL_STATE_PROMPT = """
<original_state_of_the_object description="This text shows the original state of the target object before any tool calls.">
    {original_state_of_the_object}
</original_state_of_the_object>
"""

OBJ_STATE_PROMPT = """
<current_state_of_the_object description="This text shows the current annotated state of the target object after all the previous tool calls.">
    {current_state_of_the_object}
</current_state_of_the_object>
"""

NO_TOOL_CALLS_PROMPT = """
<error>
    Please, use tools to generate the response. Response without tool calls is not allowed for this stage.
</error>
"""