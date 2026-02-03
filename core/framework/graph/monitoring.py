# core/framework/graph/monitoring.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class NodeStartEvent:
    node_id: str
    node_name: str
    input_data: dict[str, Any]


@dataclass(frozen=True)
class NodeEndEvent:
    node_id: str
    node_name: str
    success: bool
    output_data: dict[str, Any]


@dataclass(frozen=True)
class NodeErrorEvent:
    node_id: str
    node_name: str
    error: Exception


class MonitorHooks(Protocol):
    def on_node_start(self, event: NodeStartEvent) -> None: ...
    def on_node_end(self, event: NodeEndEvent) -> None: ...
    def on_node_error(self, event: NodeErrorEvent) -> None: ...
