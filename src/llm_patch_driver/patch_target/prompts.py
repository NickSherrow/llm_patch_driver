
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