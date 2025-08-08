from __future__ import annotations

"""Central logging & tracing utilities.

Provides ``log_wrapper`` decorator that attaches structured logging **and**
OpenTelemetry spans around sync or async callables.  Each value you want to
track is declared once via an :class:`ArgSpec` which specifies

* how (optionally) to aggregate/transform the raw value (`agg`)
* whether it is included in the structured log payload (`logger_data`)
* and/or attached as an OpenTelemetry span attribute (`otel_attribute`)

Example
-------

>>> @log_wrapper(
...     span_kind="llm",
...     track_args=[
...         ArgSpec("messages", logger_data="INFO", otel_attribute="messages"),
...         ArgSpec("self.user_id", agg=str, logger_data="DEBUG"),
...     ],
... )
... async def create_message(self, messages: list[Any]):
...     ...

The decorator will gather the requested metadata, write ``started`` /
``succeeded`` / ``failed`` log records and create an OpenTelemetry span if a
tracer is available via the module-level *collector* variable (see
``llm_patch_driver.config.build_log_collector``).
"""

import inspect
import sys
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TYPE_CHECKING
import json

import nanoid
from rich.pretty import pretty_repr
from rich.console import RenderableType, Console
from opentelemetry.trace import StatusCode

# Initialize a shared Rich Console instance for pretty output
_rich_console = Console()
from openinference.instrumentation._spans import OpenInferenceSpan

if TYPE_CHECKING:  # pragma: no cover
    from llm_patch_driver.config import LogCollector

__all__ = [
    "ArgSpec",
    "log_wrapper",
]


# ---------------------------------------------------------------------------
# Public dataclass describing a value to track
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ArgSpec:
    """Specification for a single value to track.

    Parameters
    ----------
    name
        Either a function parameter name (e.g. ``"payload"``) **or** an
        instance attribute expressed as ``"self.attr"``.
    agg
        Optional aggregation / transformation callable. The raw value (as passed
        to the wrapped function) is fed to this callable before routing.
    logger_data
        One of ``"DEBUG"`` / ``"INFO"`` or ``None``.  When not ``None`` the value
        will be included in the structured log payload at the specified *data
        verbosity* (currently this also dictates the log *severity*).
    otel_attribute
        Name of the attribute to attach on the OpenTelemetry span via
        :py:meth:`OpenInferenceSpan.set_attribute`. ``None`` means *do not* pass
        to OTel.
    """

    name: str
    agg: Optional[Callable[[Any], Any]] = None
    logger_level: Optional[Literal["DEBUG", "INFO"]] = None
    otel_attribute: Optional[Literal["input", "metadata"]] = None
    rich_console: Callable[..., RenderableType] | None = None

@dataclass
class ArgLogData:
    name: str
    value: Any
    logger_level: Literal["DEBUG", "INFO"] | None = None
    otel_attribute: Literal["input", "metadata"] | None = None
    rich_console: RenderableType | None = None


@dataclass
class LogData:
    id: str
    payload: List[ArgLogData]

@dataclass
class OutputFormat:
    """Output format for the log data."""
    rich_console: Callable[..., RenderableType] | None = None
    logger_level: Literal["DEBUG", "INFO"] | None = None
    otel_output: bool = False


# ---------------------------------------------------------------------------
# Decorator factory
# ---------------------------------------------------------------------------

def log_wrapper(
    log_output: OutputFormat | None = None,
    log_input: Optional[List[ArgSpec]] = None,
    log_name: Optional[str] = None,
    span_kind: Literal[
        "agent",
        "chain",
        "embedding",
        "evaluator",
        "guardrail",
        "llm",
        "reranker",
        "retriever",
        "tool",
    ] = "chain",
):
    """Decorator for structured logging + OpenTelemetry tracing.

    The decorator inspects *track_args* once at decoration time and builds fast
    lookup instructions so that per-invocation overhead is minimal.
    """

    def decorator(func: Callable):  # noqa: C901 – a bit long but self-contained
        # Retrieve the module-level LogCollector (if author followed the pattern)
        collector: "LogCollector | None" = sys.modules[func.__module__].__dict__.get(  # type: ignore[attr-defined]
            "collector"
        )
        is_async = inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        is_method = next(iter(sig.parameters), None) == "self"
        span_name = log_name if log_name is not None else func.__name__

        # ------------------------------------------------------------------
        # Build – once – the instructions required to resolve each ArgSpec
        # Each entry: (spec, index_in_args | None, is_self_attr: bool, attr_name)
        # ------------------------------------------------------------------
        positional_params = [
            pname
            for pname, p in sig.parameters.items()
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]

        fetchers: List[Tuple[ArgSpec, Optional[int], bool, str]] = []

        if log_input:
            for spec in log_input:
                key = spec.name

                if key.startswith("self."):
                    # Instance attribute: ensure we are decorating a method.
                    if not is_method:
                        raise ValueError(
                            f"track_args contains attribute '{key}' but function '{func.__name__}' "
                            "is not a method"
                        )
                    attr_name = key.split(".", 1)[1]
                    fetchers.append((spec, None, True, attr_name))
                else:
                    # Function parameter (positional or keyword)
                    if key in sig.parameters and sig.parameters[key].kind in (
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    ):
                        index = positional_params.index(key)
                    else:
                        index = None  # will be fetched from kwargs if present
                    fetchers.append((spec, index, False, key))

        # ------------------------------------------------------------------
        # Helper to collect metadata on a *single invocation*.
        # ------------------------------------------------------------------
        def gather_metadata(args: tuple[Any, ...], kwargs: dict[str, Any]) -> LogData:
            log_data: List[ArgLogData] = []

            for spec, index, is_attr, attr_name in fetchers:
                # Resolve the raw value following Python's argument rules.
                match (is_attr, spec.name in kwargs, index is not None and index < len(args)):
                    case True, _, _:
                        value = getattr(args[0], attr_name)
                    case False, True, _:
                        value = kwargs[spec.name]
                    case False, False, True:
                        value = args[index]  # type: ignore[index]
                    case _:
                        continue  # nothing to fetch

                # Apply optional aggregation.
                if spec.agg is not None:
                    try:
                        value = spec.agg(value)
                    except Exception as exc:  # pragma: no cover – defensive
                        value = f"<agg_error: {exc}>"

                arg_data = ArgLogData(name=spec.name, value=value)

                if spec.logger_level is not None:
                    arg_data.logger_level = spec.logger_level

                if spec.otel_attribute is not None:
                    arg_data.otel_attribute = spec.otel_attribute

                if spec.rich_console is not None:
                    arg_data.rich_console = spec.rich_console(value)

                log_data.append(arg_data)

            invocation_id = nanoid.generate(size=10)

            return LogData(id=invocation_id, payload=log_data)

        # ------------------------------------------------------------------
        # Logging helper (status ∈ {started, succeeded, failed}).
        # ------------------------------------------------------------------
        def log_pre(log_data: LogData):

            log_record = {
                    "status": "started",
                    "name": span_name,
                    "process_id": log_data.id,
                }

            info_payload = {
                arg_data.name: arg_data.value 
                for arg_data in log_data.payload if arg_data.logger_level == "INFO"
                }
            
            debug_payload = {
                arg_data.name: arg_data.value 
                for arg_data in log_data.payload if arg_data.logger_level == "DEBUG"
                }

            if info_payload and collector:
                info_log_record = log_record | {"log_data": info_payload}
                collector.logger.info(pretty_repr(info_log_record))

            if debug_payload and collector:
                debug_log_record = log_record | {"log_data": debug_payload}
                collector.logger.debug(pretty_repr(debug_log_record))

        def log_success(result: Any, log_data: LogData):

            if log_output and log_output.logger_level and collector:
                log_record = {
                    "status": "succeeded",
                    "name": span_name,
                    "process_id": log_data.id,
                    "result": result,
                }

                logger = collector.logger.info if log_output.logger_level == "INFO" else collector.logger.debug

                logger(pretty_repr(log_record))

        def log_failure(exc: Exception, log_data: LogData):
            if log_output and log_output.logger_level and collector:
                log_record = {
                    "status": "failed",
                    "name": span_name,
                    "process_id": log_data.id,
                    "error": str(exc),
                }

                collector.logger.info(pretty_repr(log_record))

        # ------------------------------------------------------------------
        # Span helpers
        # ------------------------------------------------------------------
        def span_pre(span: OpenInferenceSpan, log_data: LogData):

            span_meta = {
                arg_data.name: arg_data.value 
                for arg_data in log_data.payload if arg_data.otel_attribute == "metadata"
                }
            
            span_input = {
                arg_data.name: arg_data.value 
                for arg_data in log_data.payload if arg_data.otel_attribute == "input"
                }

            if span_meta:
                span.set_attribute("metadata", json.dumps(span_meta))

            if span_input:
                span.set_input(span_input)

        def span_success(span: OpenInferenceSpan, result: Any):
            span.set_status(StatusCode.OK)
            if log_output and log_output.otel_output:
                span.set_output(str(result))

        def span_failure(span: OpenInferenceSpan, exc: Exception):
            span.set_status(StatusCode.ERROR)

        # ------------------------------------------------------------------
        # Rich console helpers
        # ------------------------------------------------------------------
        def rich_pre(log_data: LogData):
            for arg_data in log_data.payload:
                if arg_data.rich_console is not None:
                    _rich_console.print(arg_data.rich_console)

        def rich_success(result: Any, log_data: LogData):
            if log_output and log_output.rich_console is not None:
                renderable = log_output.rich_console(result)
                _rich_console.print(renderable)
        
        def rich_failure(exc: Exception, log_data: LogData):
            if log_output and log_output.rich_console is not None:
                renderable = log_output.rich_console(exc)
                _rich_console.print(renderable)

        # ------------------------------------------------------------------
        # Wrapper factories (async + sync)
        # ------------------------------------------------------------------
        @wraps(func)
        async def async_wrapper(*args, **kwargs):  # type: ignore[override]
            log_data = gather_metadata(args, kwargs)

            log_pre(log_data)
            rich_pre(log_data)

            tracer = collector.tracer if collector else None

            if tracer:
                with tracer.start_as_current_span(span_name, openinference_span_kind=span_kind) as span:
                    span_pre(span, log_data)

                    try:
                        result = await func(*args, **kwargs)
                        span_success(span, result)

                    except Exception as exc:
                        span_failure(span, exc)
                        log_failure(exc, log_data)
                        rich_failure(exc, log_data)
                        raise
            else:
                try:
                    result = await func(*args, **kwargs)

                except Exception as exc:
                    log_failure(exc, log_data)
                    rich_failure(exc, log_data)
                    raise

            log_success(result, log_data)
            rich_success(result, log_data)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):  # type: ignore[override]
            log_data = gather_metadata(args, kwargs)
            result = None

            log_pre(log_data)
            rich_pre(log_data)

            tracer = collector.tracer if collector else None
            if tracer:
                with tracer.start_as_current_span(span_name, openinference_span_kind=span_kind) as span:
                    span_pre(span, log_data)
                    try:
                        result = func(*args, **kwargs)
                        span_success(span, result)
                    except Exception as exc:
                        span_failure(span, exc)
                        log_failure(exc, log_data)
                        rich_failure(exc, log_data)
                        raise
            else:
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    log_failure(exc, log_data)
                    rich_failure(exc, log_data)
                    raise

            log_success(result, log_data)
            rich_success(result, log_data)
            return result

        return async_wrapper if is_async else sync_wrapper

    return decorator
