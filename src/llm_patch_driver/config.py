import logging
from typing import Literal, Optional, Tuple, List
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, PrivateAttr
from phoenix.otel import TracerProvider
from openinference.instrumentation import OITracer
import rich.traceback

rich.traceback.install()

@dataclass
class LogCollector:
    module_name: str
    logger: logging.Logger
    tracer: OITracer | None = None

class LibConfig(BaseModel):

    _otel_provider: Optional[TracerProvider] = None
    _log_collectors: List[LogCollector] = PrivateAttr(default_factory=list)

    @property
    def otel_provider(self) -> TracerProvider | None:
        return self._otel_provider
    
    @otel_provider.setter
    def otel_provider(self, provider: TracerProvider):
        self._otel_provider = provider
        for collector in self._log_collectors:
            collector.tracer = provider.get_tracer(collector.module_name)

    def build_log_collector(self, module_name: str) -> LogCollector:
        collector = LogCollector(module_name, logging.getLogger(module_name))
        if self.otel_provider:
            collector.tracer = self.otel_provider.get_tracer(module_name)
        self._log_collectors.append(collector)
        return collector

config = LibConfig()