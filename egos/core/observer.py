"""Observer stage: evaluate run quality and produce a confidence score."""
from __future__ import annotations

import time

from egos.core.models import ExecutionNode, NodeStatus


class ObserverStage:
    """Scores the execution and emits a final observation node."""

    def run(
        self,
        executor_node: ExecutionNode,
        memory_node: ExecutionNode,
        policy_node: ExecutionNode,
    ) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(
            stage="observer",
            action="evaluate",
            parent_id=executor_node.node_id,
        )

        results = executor_node.output.get("results", [])
        total = len(results)
        succeeded = sum(1 for r in results if r.get("status") == "ok")
        blocked = sum(1 for r in results if r.get("status") == "blocked")
        failed = sum(1 for r in results if r.get("status") == "error")

        confidence = round(succeeded / total, 2) if total > 0 else 0.0
        any_blocked = policy_node.output.get("any_blocked", False)

        node.input = {"total": total, "succeeded": succeeded, "blocked": blocked, "failed": failed}
        node.output = {
            "confidence": confidence,
            "success": failed == 0,
            "any_blocked": any_blocked,
            "summary": self._summarize(succeeded, failed, blocked, confidence),
        }
        node.status = NodeStatus.SUCCESS if failed == 0 else NodeStatus.FAILED
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node

    @staticmethod
    def _summarize(succeeded: int, failed: int, blocked: int, confidence: float) -> str:
        parts: list[str] = []
        if succeeded:
            parts.append(f"{succeeded} step(s) succeeded")
        if failed:
            parts.append(f"{failed} step(s) failed")
        if blocked:
            parts.append(f"{blocked} step(s) blocked by policy")
        parts.append(f"confidence={confidence:.0%}")
        return ", ".join(parts)
