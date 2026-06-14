"""Core data models for EGOS execution graph."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"  # policy denied


@dataclass
class ExecutionNode:
    """A single traced step in an execution graph."""

    node_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    trace_id: str = ""
    stage: str = ""          # context | planner | policy | executor | memory | observer
    action: str = ""
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    parent_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "trace_id": self.trace_id,
            "stage": self.stage,
            "action": self.action,
            "input": self.input,
            "output": self.output,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp,
            "duration_ms": round(self.duration_ms, 2),
            "meta": self.meta,
        }


@dataclass
class ExecutionGraph:
    """Complete execution graph for one agent run."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal: str = ""
    nodes: list[ExecutionNode] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    def add_node(self, node: ExecutionNode) -> None:
        node.trace_id = self.trace_id
        self.nodes.append(node)

    def finish(self) -> None:
        self.finished_at = time.time()

    @property
    def duration_ms(self) -> float:
        if self.finished_at is None:
            return 0.0
        return round((self.finished_at - self.started_at) * 1000, 2)

    @property
    def success(self) -> bool:
        return any(n.stage == "observer" and n.status == NodeStatus.SUCCESS for n in self.nodes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "goal": self.goal,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "nodes": [n.to_dict() for n in self.nodes],
        }
