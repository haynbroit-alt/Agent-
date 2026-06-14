"""Memory stage: persist execution results for future context."""
from __future__ import annotations

import time
from typing import Any

from egos.core.models import ExecutionNode, NodeStatus


class MemoryStage:
    """Stores executor results into an in-process memory store (or external)."""

    def __init__(self, store: dict[str, Any] | None = None) -> None:
        self._store: dict[str, Any] = store if store is not None else {}

    def run(self, executor_node: ExecutionNode) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(
            stage="memory",
            action="store",
            parent_id=executor_node.node_id,
        )
        results = executor_node.output.get("results", [])
        node.input = {"results_count": len(results)}

        entries_stored = 0
        for r in results:
            if r.get("status") == "ok" and r.get("output") is not None:
                key = f"{executor_node.trace_id}:{r['tool']}"
                self._store[key] = r["output"]
                entries_stored += 1

        node.output = {"entries_stored": entries_stored, "total_entries": len(self._store)}
        node.status = NodeStatus.SUCCESS
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node

    def recall(self, trace_id: str, tool: str) -> Any | None:
        return self._store.get(f"{trace_id}:{tool}")

    def all(self) -> dict[str, Any]:
        return dict(self._store)
