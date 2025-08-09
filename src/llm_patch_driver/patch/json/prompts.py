JSON_ANNOTATION_TEMPLATE = """
<annotation_syntax>
The JSON was annotated with <a> and <i> tags. That was made to help you navigate the JSON data.
The <a> tag means 'anchor' and the <i> tag means 'index'. They are temporary tags that are visible only to you.
<a> tags are added to all keys in the JSON. The <i> tag is added to all elements in all arrays.

    Example: 
    - {{"sample_key": 1}} -> {{<a=1 k=sample_key>: 1}}
    - [A, B, C] -> [<i=1 v=A>, <i=2 v=B>, <i=3 v=C>]

The real JSON does not have any annotations. They are visible only to you.

This version of the JSON is the current state of the object.
</annotation_syntax>

<annotated_json>
```json
{object_content}
```
</annotated_json>

<annotation_syntax>
The JSON was annotated with <a> and <i> tags. That was made to help you navigate the JSON data.
The <a> tag means 'anchor' and the <i> tag means 'index'. They are temporary tags that are visible only to you.
<a> tags are added to all keys in the JSON. The <i> tag is added to all elements in all arrays.

    Example: 
    - {{"sample_key": 1}} -> {{<a=1 k=sample_key>: 1}}
    - [A, B, C] -> [<i=1 v=A>, <i=2 v=B>, <i=3 v=C>]

The real JSON does not have any annotations. They are visible only to you.

This version of the JSON is the current state of the object.
</annotation_syntax>
"""

JSON_PATCH_SYNTAX = """
<patch description="A patch is a JSON object that will be parsed and used to modify the JSON document.">
    <overview>
        You do NOT provide JSON Pointer paths directly. Instead, you use:
        - <a_id>: the id of an anchor from the annotated JSON (<a=ID k=key>), which resolves to an internal JSON Pointer path.
        - <i_id> (optional): a 1-based index that targets an item inside the array at the <a_id> path.

        Operations:
        - op = "replace": Replace the entire value stored at the key identified by <a_id>. Do NOT use <i_id> here.
        - op = "add": Add a value either at the key identified by <a_id> or into the array at that key using <i_id>.
        - op = "remove": Remove a key (no <i_id>) or remove an array item (with <i_id>).

        Requirements:
        - "op" and "a_id" are always required.
        - "value" is required for "add" and "replace"; for "remove" it MUST be null.
        - For arrays, <i_id> is 1-based. Internally it is converted to 0-based (i_id - 1).
    </overview>

    <fields>
        <field name="op">
            <description>The operation to perform.</description>
            <data_type>Literal["add", "remove", "replace"]</data_type>
            <notes>
                - Use "replace" to overwrite the value of a key. Do not include <i_id>.
                - Use "add" to insert into arrays (with <i_id>) or to set a value at a key.
                - Use "remove" to delete a key or an array element. For remove, set "value" to null.
            </notes>
        </field>

        <field name="a_id">
            <description>The anchor id of the key to operate on. This id comes from the <a=ID k=...> tags in the annotated JSON.</description>
            <data_type>int</data_type>
            <example>
                If the annotation shows {{"<a=12 k=roles>": [ ... ]}}, then a_id=12 refers to the "roles" key.
            </example>
        </field>

        <field name="i_id" optional="true">
            <description>Item index inside the array at <a_id>. Only for array operations ("add" and "remove"). 1-based.</description>
            <data_type>int | null</data_type>
            <notes>
                - Omit or set to null for key-level operations or when op is "replace".
                - i_id=1 targets the first element (internally index 0), i_id=2 the second, etc.
                - To append to an array of length N, use i_id = N + 1.
            </notes>
        </field>

        <field name="value">
            <description>The JSON value for the operation.</description>
            <data_type>any JSON (null for remove)</data_type>
            <rules>
                - Required and non-null for "add" and "replace".
                - Must be null for "remove".
            </rules>
        </field>
    </fields>

    <how_to_build>
        <case name="Replace the value of a key">
            <when>
                You see a key annotated as <a=2 k=name> and want to change its value from "Alice" to "Alicia".
            </when>
            <patch_example>
                {{"op": "replace", "a_id": 2, "i_id": null, "value": "Alicia"}}
            </patch_example>
            <notes>
                - Do not include i_id (omit or set to null) for replace.
            </notes>
        </case>

        <case name="Insert a new item into an array">
            <when>
                You see an array annotated under <a=3 k=roles>: [<i=1 v=admin>, <i=2 v=editor>]. Insert "viewer" as the 3rd item.
            </when>
            <patch_example>
                {{"op": "add", "a_id": 3, "i_id": 3, "value": "viewer"}}
            </patch_example>
            <notes>
                - i_id is 1-based; i_id=3 inserts at internal index 2.
                - To append to the end, use i_id = current_length + 1.
            </notes>
        </case>

        <case name="Remove a key">
            <when>
                You see a key annotated as <a=2 k=name> and want to delete it entirely.
            </when>
            <patch_example>
                {{"op": "remove", "a_id": 2, "i_id": null, "value": null}}
            </patch_example>
            <notes>
                - Removing a key deletes it from the object.
            </notes>
        </case>

        <case name="Remove an item from an array">
            <when>
                You see an array under <a=3 k=roles> and want to remove the first item.
            </when>
            <patch_example>
                {{"op": "remove", "a_id": 3, "i_id": 1, "value": null}}
            </patch_example>
            <notes>
                - i_id=1 targets the first element.
            </notes>
        </case>

        <case name="Add a complex object as an array item">
            <when>
                You see <a=10 k=items>: [] and you want to insert {{"id": 1, "qty": 2}} as the first element.
            </when>
            <patch_example>
                {{"op": "add", "a_id": 10, "i_id": 1, "value": {{"id": 1, "qty": 2}}}}
            </patch_example>
        </case>
    </how_to_build>
</patch>
"""

ANNOTATION_PLACEHOLDER = """
<current_state_of_the_text>
    <annotated_text>
        THIS VERSION OF THE JSON IS NO LONGER ACTUAL. IT WAS REMOVED FROM THE MESSAGE HISTORY TO SAVE SPACE.
        BELOW IN THE CONVERSATION YOU WILL SEE THE CURRENT STATE OF THE OBJECT. IGNORE THIS ONE.
    </annotated_text>
</current_state_of_the_text>
"""