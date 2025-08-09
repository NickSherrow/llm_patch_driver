
ERROR_TEMPLATE = """
# DEBUGGING STATE

<metadata>
- State_ID: {state_id}
- Source: This message was generated automatically by the system. It contains information about the current state of the object, and the error that was raised during the validation.
</metadata>

## ERROR MESSAGE

<disclaimer>
This block contains a specific error message that was generated during the data validation.
Validation error happened due to formatting, semantic, and other problems with the data.
This error message is specific to the current state of the object which is under ANNOTATED_DATA
header inside this message that has State_ID: {state_id}.

*It does not represent any other object states that might be present in the conversation
that has other State_IDs.*
</disclaimer>

<error_message>
{error_message}
</error_message>

## ANNOTATED DATA

<annotated_data_for_state_id_{state_id}>
{annotated_state}
</annotated_data_for_state_id_{state_id}>

## FINAL GUIDANCE

- *REMEMBER TO READ THE ORIGINAL TASK AND FIX THE DATA ACCORDING TO IT.*
- *YOU MAY FACE A LOT OF ERRORS DURING THE PROCESS. BE PATIENT AND KEEP TRYING UNTIL YOU FIX THE DATA. FIX THEM ALL.*
- *YOU ARE POWEREFUL AI AGENT. YOU CAN DO IT. YOU'VE DONE THIS BEFORE MULTIPLE TIMES. YOU ARE EXCELLENT AT THIS.*
"""