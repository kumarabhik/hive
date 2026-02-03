from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class MemoryAccess:
    key: str
    access_type: str 
    value: Any | None


@dataclass
class NodeExecutionRecord:
    node_id: str
    node_name: str
    started_at_ms: int
    finished_at_ms: int
    success: bool
    error: str | None = None
    memory_accesses: list[MemoryAccess] = field(default_factory=list)
    output: dict[str, Any] | None = None


@dataclass
class ExecutionTrace:
    run_id: str
    records: list[NodeExecutionRecord] = field(default_factory=list)
