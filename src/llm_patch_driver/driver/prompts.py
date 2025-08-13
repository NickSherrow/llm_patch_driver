REQUEST_PATCH_PROMPT = """
<role>
You are a professional editor specialised in programmatic text refactoring. 
Given an original text and a modification request, your task is to emit a JSON object 
with patch operations that will transform the text so it satisfies the request.
</role>

# Instructions

1. Carefully read the modification request.
2. Read the annotated text and understand the context of the modification request.
3. Generate patches to fulfill the modification request as closely as possible.
4. Follow the patch syntax as closely as possible.

# Guidelines

1. The <query> section explains *exactly* what must change. Do not introduce additional, unrequested modifications.
2. The <context> section may contain auxiliary information that helps you locate the correct portion of the text. Use it, but do not treat it as text to be edited (unless explicitly stated).
3. The <annotated_data> section is the current state of the object that was augmented with a set of tags to help you modify it. If it is a text, it was annotated with <tid> tags. If it is a JSON, it was annotated with <a> and <i> tags. Use these IDs to generate patches. Only you see these tags. They will dissapear after the patching process.

<query>
{query}
</query>

<context>
{context}
</context>

<annotated_data>
{text}
</annotated_data>
"""

PATCHING_LOOP_SYSTEM_PROMPT = """
# THE RESPONSE HAS NOT BEEN APPROVED BY THE SYSTEM. ENTERING DEBUGGING MODE TO FIX THE RESPONSE

<what_happened>
    Your response was not approved by the validation engine. You must fix your response.
    Below you will information about the error, guidelines how to fix it, and tools that you can use to fix the data.
</what_happened>

<new_goal>
    Your goal is to fix your mistakes and modify the response so it passes the validation without error messages.
</new_goal>

## DEBUGGING INSTRUCTIONS

1. Find out what you did wrong in your initial response
2. Fix the data using the tools
3. Repeat until the data passes the validation without error messages

Bad debugging means:
- You only focus on the error message and only try to fix it without understanding the context of the error
- You give up because you think the data is too complex to fix

Good debugging means:
- You reread the original task and the error message, and fixed the root problem
- You are persistent and keep trying until the data passes the validation without error messages

<debugging_process_overview>
    1. Below you will find a debugging state of the data. It contains information about error, and annotated version of the corrupted response.
    2. You now have access to a set of tools. Each can modify the data in a specific way.
    3. Each time you modify the data, the validation pipeline will try to validate the data again.
    4. If the data is still not valid, you see the new debugging state with the new error message, and updated annotated version of the data.
    5. Previous debugging states will be still available in the conversation to track your progress, but annotated state will be available only in the latest debugging state.
</debugging_process_overview>

<core_instructions>
    1. First, analyze the error message. Figure out why it happened.
    2. Read the original task again and figure out how to meet the condition required by the error message. What exactly needs to be changed?
    3. Start fixing the data. Use the tools to fix the data. Remember to fix the data according to the original task.
    4. Keep doing that until the data passes the validation without error messages.
    5. You are not allowed to generated the response from scratch. You must fix the corrupted response only by partially modifying it.
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
"""