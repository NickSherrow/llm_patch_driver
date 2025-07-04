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

ERROR_TEMPLATE = """
<debugging_state>
    <metadata>
        State_ID: {state_id}
        Source: This message was generated automatically by the system. It contains information about the current state of the object, and the error that was raised during the validation.
    </metadata>

    <validation_error>
        <error_context>
            This block contains a specific error message that was generated during the data validation.
            Validation error happened due to formatting, semantic, and other problems with the data.
            This error message is specific to the current state of the object which is inside 
            <current_state_of_the_text> tag inside this message that has State_ID: {state_id}.

            It does not represent any other object states that might be present in the conversation
            that has other State_IDs.
        </error_context>

        <error_message>
            {error_message}
        </error_message>
    </validation_error>

    {annotated_state}
</debugging_state>
"""

ANNOTATION_PLACEHOLDER = """
<current_state_of_the_text>
    <annotated_text>
        THIS VERSION OF THE TEXT IS NO LONGER ACTUAL. IT WAS REMOVED FROM THE MESSAGE HISTORY TO SAVE SPACE.
        BELOW IN THE CONVERSATION YOU WILL SEE THE CURRENT STATE OF THE OBJECT. IGNORE THIS ONE.
    </annotated_text>
</current_state_of_the_text>
"""

STR_ANNOTATION_TEMPLATE = """
<current_state_of_the_text>
    The text was annotated with <tid> tags. Each tid is a unique identifier for a sentence in the text.
    That was made to help you modify the text. To modify the text, just provide a list of tids and the required modification.
    The final text will not have any annotations. This is just a temporary view to help you modify the text.

    This version of the text is the current state of the object.

        <annotated_text>
            {text}
        </annotated_text>

    This version of the text is the current state of the object.

    The text was annotated with <tid> tags. Each tid is a unique identifier for a sentence in the text.
    That was made to help you modify the text. To modify the text, just provide a list of tids and the required modification.
    The final text will not have any annotations. This is just a temporary view to help you modify the text.
</current_state_of_the_text>
    """

STR_PATCH_SYNTAX = """
    <patch description="A patch is a JSON object that will be parsed and then used to modify the text.">
        <fields>
            <field name="tids">
                <description>A list of <tid> tags. Each tid represents a target sentence in the text.</description>
                <data_type>List[str]</data_type>
                <data_format>
                    <example>
                        ["1_1", "1_2", "1_3"]
                    </example>
                    <explanation>
                        1_2: second sentence in the first line
                        2_1: first sentence in the second line
                    </explanation>
                </data_format>
            </field>
            <field name="operation">
                <description>The operation to perform on the target sentences. Must be one of the following: "ReplaceOp", "DeleteOp", "InsertAfterOp".</description>
                    <ReplaceOp> 
                     Description: Performs a pattern substitution on the target sentences using str.replace(pattern, replacement) in Python."
                     Notes: no count limit for the number of replacements.
                     Fields:
                        <field name="type">
                            <description>The type of the operation. Must be "replace".</description>
                            <data_type>Literal["replace"]</data_type>
                        </field>
                        <field name="pattern">
                            <description>The pattern to replace. Will be parsed as a regex.</description>
                            <data_type>str</data_type>
                        </field>
                        <field name="replacement">
                            <description>The replacement text.</description>
                            <data_type>str</data_type>
                        </field>
                    </ReplaceOp>
                    <DeleteOp>
                        Description: Deletes the target sentences.
                        Fields:
                            <field name="type">
                                <description>The type of the operation. Must be "delete".</description>
                                <data_type>Literal["delete"]</data_type>
                            </field>
                    </DeleteOp>
                    <InsertAfterOp>
                        Description: Inserts a new line after the line of the last tid.
                        Fields:
                            <field name="type">
                                <description>The type of the operation. Must be "insert_after".</description>
                                <data_type>Literal["insert_after"]</data_type>
                            </field>
                            <field name="text">
                                <description>The text to insert after the line of the last tid.</description>
                                <data_type>str</data_type>
                            </field>
                    </InsertAfterOp>
                </data_format>
            </field>
        </fields>
    </patch>
    """

JSON_PATCH_SYNTAX = """
    <patch description="A patch is a JSON object that will be parsed and then used to modify the text.">
        <fields>
            <field name="path">
                <description>The path to the target object.</description>
                <data_type>str</data_type>
            </field>
        </fields>
    </patch>
    """

JSON_ANNOTATION_TEMPLATE = """
<current_state_of_the_text>
    The JSON was annotated with <a> and <i> tags. That was made to help you navigate the JSON data.
    The <a> tag means 'anchor' and the <i> tag means 'index'. They are temporary tags that are visible only to you.
    <a> tags are added to all keys in the JSON. The <i> tag is added to all elements in all arrays.

    Example: 
    - {{"sample_key": 1}} -> {{<a=1 k=sample_key>: 1}}
    - [A, B, C] -> [<i=1 v=A>, <i=2 v=B>, <i=3 v=C>]

    The real JSON does not have any annotations. They are visible only to you.

    This version of the JSON is the current state of the object.

        <annotated_json>
            {text}
        </annotated_json>

    The JSON was annotated with <a> and <i> tags. That was made to help you navigate the JSON data.
    The <a> tag means 'anchor' and the <i> tag means 'index'. They are temporary tags that are visible only to you.
    <a> tags are added to all keys in the JSON. The <i> tag is added to all elements in all arrays.

    Example: 
    - {{"sample_key": 1}} -> {{<a=1 k=sample_key>: 1}}
    - [A, B, C] -> [<i=1 v=A>, <i=2 v=B>, <i=3 v=C>]

    The real JSON does not have any annotations. They are visible only to you.

    This version of the JSON is the current state of the object.
</current_state_of_the_text>
    """