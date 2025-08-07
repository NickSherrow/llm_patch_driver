STR_ANNOTATION_TEMPLATE = """
<current_state_of_the_text>
    The text was annotated with <tid> tags. Each tid is a unique identifier for a sentence in the text.
    That was made to help you modify the text. To modify the text, just provide a list of tids and the required modification.
    The final text will not have any annotations. This is just a temporary view to help you modify the text.

    This version of the text is the current state of the object.

        <annotated_text>
            {object_content}
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

ANNOTATION_PLACEHOLDER = """
<current_state_of_the_text>
    <annotated_text>
        THIS VERSION OF THE TEXT IS NO LONGER ACTUAL. IT WAS REMOVED FROM THE MESSAGE HISTORY TO SAVE SPACE.
        BELOW IN THE CONVERSATION YOU WILL SEE THE CURRENT STATE OF THE OBJECT. IGNORE THIS ONE.
    </annotated_text>
</current_state_of_the_text>
"""
