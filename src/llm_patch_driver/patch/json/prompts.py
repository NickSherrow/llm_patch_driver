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
            {object_content}
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

ANNOTATION_PLACEHOLDER = """
<current_state_of_the_text>
    <annotated_text>
        THIS VERSION OF THE TEXT IS NO LONGER ACTUAL. IT WAS REMOVED FROM THE MESSAGE HISTORY TO SAVE SPACE.
        BELOW IN THE CONVERSATION YOU WILL SEE THE CURRENT STATE OF THE OBJECT. IGNORE THIS ONE.
    </annotated_text>
</current_state_of_the_text>
"""