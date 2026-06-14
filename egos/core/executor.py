"""Executor stage: run each allowed step via the tool registry."""
from __future__ import annotations

import time

from egos.core.models import ExecutionNode, NodeStatus
from egos.tools.registry import ToolRegistry


class ExecutorStage:
    """Runs the policy-approved steps and collects results."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def run(self, policy_node: ExecutionNode) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(
            stage="executor",
            action="run_steps",
            parent_id=policy_node.node_id,
        )
        evaluated = policy_node.output.get("evaluated_steps", [])
        node.input = {"steps_count": len(evaluated)}

        results: list[dict] = []
        failed = False

        for step in evaluated:
            if not step.get("allowed", False):
                results.append({
                    "tool": step["tool"],
                    "status": "blocked",
                    "output": None,
                    "error": step.get("reason", "policy_blocked"),
                })
                continue

            tool = self._registry.get(step["tool"])
            if tool is None:
                results.append({
                    "tool": step["tool"],
                    "status": "error",
                    "output": None,
                    "error": "tool_not_found",
                })
                failed = True
                continue

            try:
                result = tool.run(**step.get("args", {}))
                results.append({"tool": step["tool"], "status": "ok", "output": result, "error": None})
            except Exception as exc:  # noqa: BLE001
                results.append({"tool": step["tool"], "status": "error", "output": None, "error": str(exc)})
                failed = True

        node.output = {"results": results}
        node.status = NodeStatus.FAILED if failed else NodeStatus.SUCCESS
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node
