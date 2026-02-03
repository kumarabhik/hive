import pytest
from unittest.mock import MagicMock

from framework.graph.executor import GraphExecutor
from framework.graph.node import NodeSpec, NodeProtocol, NodeContext, NodeResult
from framework.graph.edge import GraphSpec
from framework.graph.goal import Goal
from framework.runtime.core import Runtime
from framework.graph.monitoring import MonitorHooks, NodeStartEvent, NodeEndEvent, NodeErrorEvent


class CaptureMonitor(MonitorHooks):
    def __init__(self) -> None:
        self.events: list[str] = []

    def on_node_start(self, event: NodeStartEvent) -> None:
        self.events.append(f"start:{event.node_id}:{event.node_name}")

    def on_node_end(self, event: NodeEndEvent) -> None:
        self.events.append(f"end:{event.node_id}:{event.node_name}:{event.success}")

    def on_node_error(self, event: NodeErrorEvent) -> None:
        self.events.append(f"error:{event.node_id}:{event.node_name}")


class SuccessNode(NodeProtocol):
    async def execute(self, ctx: NodeContext) -> NodeResult:
        return NodeResult(success=True, output={"ok": True})


@pytest.fixture
def runtime():
    runtime = MagicMock(spec=Runtime)
    runtime.start_run = MagicMock(return_value="test_run_id")
    runtime.decide = MagicMock(return_value="test_decision_id")
    runtime.record_outcome = MagicMock()
    runtime.end_run = MagicMock()
    runtime.report_problem = MagicMock()
    runtime.set_node = MagicMock()
    return runtime


@pytest.mark.asyncio
async def test_monitor_hooks_fire_for_node_lifecycle(runtime):
    node_spec = NodeSpec(
        id="n1",
        name="Node 1",
        description="test node",
        node_type="function",
        output_keys=["ok"],
        max_retries=1,
    )

    graph = GraphSpec(
        id="g1",
        goal_id="goal1",
        name="Test Graph",
        entry_node="n1",
        nodes=[node_spec],
        edges=[],
        terminal_nodes=["n1"],
    )

    goal = Goal(id="goal1", name="Goal", description="test")

    monitor = CaptureMonitor()
    executor = GraphExecutor(runtime=runtime, monitor=monitor)
    executor.register_node("n1", SuccessNode())

    result = await executor.execute(graph, goal, {})

    assert result.success is True
    assert monitor.events[0].startswith("start:n1:Node 1")
    assert monitor.events[-1].startswith("end:n1:Node 1:True")
