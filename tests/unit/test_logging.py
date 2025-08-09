"""Unit tests for logging decorator minimal behavior.

We assert that the decorator wraps an async function and returns its result.
We don't assert on external logging side effects; just that no exceptions occur
and that the function executes.
"""

import asyncio

from llm_patch_driver.logging import log_wrapper, ArgSpec, OutputFormat


@log_wrapper(
    log_input=[ArgSpec(name="x", logger_level="INFO")],
    log_output=OutputFormat(logger_level="INFO"),
    span_kind="tool",
)
async def add_one(x: int) -> int:
    return x + 1


def test_log_wrapper_async_function_executes():
    result = asyncio.run(add_one(41))
    assert result == 42

