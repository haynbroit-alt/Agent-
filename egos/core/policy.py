"""Policy stage: safety and permission gate before execution."""
from __future__ import annotations

import time

from egos.core.models import ExecutionNode, NodeStatus


# Tools/actions that are never allowed, regardless of context
_BLOCKED_TOOLS = frozenset({"rm_rf", "drop_db", "format_disk"})

# Patterns that trigger a block on raw goal text
_BLOCKED_PATTERNS = (
    "delete all",
    "rm -rf",
    "format c:",
    "shutdown",
    "drop table",
)


class PolicyStage:
    """Evaluates a plan against safety rules and returns allow/deny per step."""

    def run(self, plan_node: ExecutionNode) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(
            stage="policy",
            action="evaluate",
            parent_id=plan_node.node_id,
        )
        node.input = {"steps": plan_node.output.get("steps", [])}

        evaluated: list[dict] = []
        any_blocked = False

        for step in plan_node.output.get("steps", []):
            tool = step.get("tool", "")
            goal_text = step.get("description", "").lower()

            blocked = tool in _BLOCKED_TOOLS or any(p in goal_text for p in _BLOCKED_PATTERNS)
            evaluated.append({**step, "allowed": not blocked, "reason": "blocked_pattern" if blocked else "ok"})
            if blocked:
                any_blocked = True

        node.output = {"evaluated_steps": evaluated, "any_blocked": any_blocked}
        node.status = NodeStatus.BLOCKED if any_blocked else NodeStatus.SUCCESS
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node
