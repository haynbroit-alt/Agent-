"""Planner stage: decompose goal into ordered execution steps."""
from __future__ import annotations

import time

from egos.core.models import ExecutionNode, NodeStatus
from egos.tools.registry import ToolRegistry


class PlannerStage:
    """Produces an ordered list of (tool, args) steps from a context node."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def run(self, context_node: ExecutionNode) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(
            stage="planner",
            action="decompose",
            parent_id=context_node.node_id,
        )
        node.input = {"context": context_node.output}

        goal: str = context_node.output.get("goal", "")
        intent: str = context_node.output.get("intent", "general")
        steps = self._plan(goal, intent)

        node.output = {"steps": steps, "total": len(steps)}
        node.status = NodeStatus.SUCCESS
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node

    # Heuristic mappings: (pattern, command template)
    # Replace with LLM tool-call for production
    _SHELL_PATTERNS: list[tuple[str, str]] = [
        ("list files in", "ls {target}"),
        ("list files", "ls {target}"),
        ("show files in", "ls {target}"),
        ("find files in", "ls {target}"),
        ("show current directory", "pwd"),
        ("current directory", "pwd"),
        ("current date", "date"),
        ("show date", "date"),
        ("system info", "uname -a"),
        ("ls ", "ls {target}"),
    ]

    def _plan(self, goal: str, intent: str) -> list[dict]:
        """Return a list of step dicts: {tool, args, description}."""
        lower = goal.lower().strip()
        steps: list[dict] = []

        # Try to map natural language to a shell command
        for pattern, cmd_template in self._SHELL_PATTERNS:
            if pattern in lower:
                # Extract the target (everything after the pattern keyword)
                after = lower.split(pattern, 1)[-1].strip()
                target = after if after else "."
                command = cmd_template.format(target=target)
                steps.append({
                    "tool": "shell",
                    "args": {"command": command},
                    "description": f"shell: {command}",
                })
                break

        # Check for explicit shell command passthrough (starts with known binary)
        if not steps:
            first_word = lower.split()[0] if lower.split() else ""
            _SAFE_BINS = {"ls", "cat", "echo", "pwd", "find", "grep", "wc", "head", "tail", "date", "uname"}
            if first_word in _SAFE_BINS:
                steps.append({
                    "tool": "shell",
                    "args": {"command": goal},
                    "description": f"shell: {goal[:60]}",
                })

        if not steps:
            steps = [{"tool": "echo", "args": {"text": goal}, "description": goal[:80]}]

        return steps
