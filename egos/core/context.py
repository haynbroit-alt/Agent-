"""Context stage: parse and enrich the user goal."""
from __future__ import annotations

import time
from typing import Any

from egos.core.models import ExecutionNode, NodeStatus


class ContextStage:
    """Parses user intent into a structured context dict."""

    def run(self, goal: str, session: dict[str, Any]) -> ExecutionNode:
        t0 = time.perf_counter()
        node = ExecutionNode(stage="context", action="parse_intent")
        node.input = {"goal": goal, "session_keys": list(session.keys())}

        # Derive intent type (simple heuristic — swap with LLM call for prod)
        intent = self._classify(goal)

        node.output = {
            "intent": intent,
            "goal": goal,
            "tokens_estimate": len(goal.split()),
        }
        node.status = NodeStatus.SUCCESS
        node.duration_ms = (time.perf_counter() - t0) * 1000
        return node

    @staticmethod
    def _classify(goal: str) -> str:
        lower = goal.lower()
        if any(w in lower for w in ["list", "show", "find", "get", "search"]):
            return "query"
        if any(w in lower for w in ["create", "write", "make", "generate"]):
            return "create"
        if any(w in lower for w in ["run", "execute", "call"]):
            return "execute"
        return "general"
