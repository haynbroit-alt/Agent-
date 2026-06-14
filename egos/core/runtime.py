"""EGOS Runtime: the main execution loop Context → Planner → Policy → Executor → Memory → Observer."""
from __future__ import annotations

from typing import Any

from egos.core.context import ContextStage
from egos.core.executor import ExecutorStage
from egos.core.memory import MemoryStage
from egos.core.models import ExecutionGraph
from egos.core.observer import ObserverStage
from egos.core.planner import PlannerStage
from egos.core.policy import PolicyStage
from egos.tools.registry import ToolRegistry
from egos.trace.logger import TraceLogger


class Runtime:
    """
    EGOS Runtime.

    Each call to `run()` produces a fully traced ExecutionGraph.
    The graph can be inspected, replayed, or exported to JSONL.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        logger: TraceLogger | None = None,
        memory_store: dict[str, Any] | None = None,
    ) -> None:
        self._registry = registry or ToolRegistry.default()
        self._logger = logger or TraceLogger()
        self._memory = MemoryStage(store=memory_store)

        self._context_stage = ContextStage()
        self._planner_stage = PlannerStage(self._registry)
        self._policy_stage = PolicyStage()
        self._executor_stage = ExecutorStage(self._registry)
        self._observer_stage = ObserverStage()

    def run(self, goal: str, session: dict[str, Any] | None = None) -> ExecutionGraph:
        """Execute `goal` and return the full traced ExecutionGraph."""
        session = session or {}
        graph = ExecutionGraph(goal=goal)
        self._logger.begin(graph)

        # --- Stage 1: Context ---
        ctx_node = self._context_stage.run(goal, session)
        graph.add_node(ctx_node)
        self._logger.node(ctx_node)

        # --- Stage 2: Planner ---
        plan_node = self._planner_stage.run(ctx_node)
        graph.add_node(plan_node)
        self._logger.node(plan_node)

        # --- Stage 3: Policy ---
        policy_node = self._policy_stage.run(plan_node)
        graph.add_node(policy_node)
        self._logger.node(policy_node)

        # --- Stage 4: Executor ---
        exec_node = self._executor_stage.run(policy_node)
        graph.add_node(exec_node)
        self._logger.node(exec_node)

        # --- Stage 5: Memory ---
        mem_node = self._memory.run(exec_node)
        graph.add_node(mem_node)
        self._logger.node(mem_node)

        # --- Stage 6: Observer ---
        obs_node = self._observer_stage.run(exec_node, mem_node, policy_node)
        graph.add_node(obs_node)
        self._logger.node(obs_node)

        graph.finish()
        self._logger.end(graph)
        return graph

    @property
    def memory(self) -> MemoryStage:
        return self._memory
