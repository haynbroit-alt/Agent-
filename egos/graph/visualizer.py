"""Visualize an ExecutionGraph as ASCII art or Mermaid flowchart."""
from __future__ import annotations

from egos.core.models import ExecutionGraph, NodeStatus

_STATUS_ICON = {
    NodeStatus.SUCCESS: "✓",
    NodeStatus.FAILED:  "✗",
    NodeStatus.BLOCKED: "⊘",
    NodeStatus.RUNNING: "…",
    NodeStatus.PENDING: "○",
}

_STAGE_ORDER = ["context", "planner", "policy", "executor", "memory", "observer"]


def render_ascii(graph: ExecutionGraph) -> str:
    """Return a compact ASCII pipeline view of the graph."""
    lines: list[str] = [
        f"trace: {graph.trace_id}  goal: {graph.goal[:60]}",
        "",
    ]

    by_stage: dict[str, list] = {}
    for node in graph.nodes:
        by_stage.setdefault(node.stage, []).append(node)

    stages = [s for s in _STAGE_ORDER if s in by_stage]
    width = max(len(s) for s in stages) + 6

    for i, stage in enumerate(stages):
        nodes = by_stage[stage]
        icon = _STATUS_ICON.get(nodes[-1].status, "?")
        ms = round(sum(n.duration_ms for n in nodes), 1)
        label = f"[{icon}] {stage.upper():<12} {ms:>7.1f}ms"
        lines.append(label)
        if i < len(stages) - 1:
            lines.append("      │")

    if graph.finished_at:
        lines.append("")
        status = "SUCCESS" if graph.success else "FAILED"
        lines.append(f"  ► {status}  total={graph.duration_ms:.1f}ms  nodes={len(graph.nodes)}")

    return "\n".join(lines)


def render_mermaid(graph: ExecutionGraph) -> str:
    """Return a Mermaid flowchart definition (paste into mermaid.live)."""
    lines = ["flowchart TD"]

    by_stage: dict[str, list] = {}
    for node in graph.nodes:
        by_stage.setdefault(node.stage, []).append(node)

    stages = [s for s in _STAGE_ORDER if s in by_stage]
    ids: list[str] = []

    for stage in stages:
        nodes = by_stage[stage]
        icon = _STATUS_ICON.get(nodes[-1].status, "?")
        ms = round(sum(n.duration_ms for n in nodes), 1)
        nid = stage.upper()
        ids.append(nid)
        lines.append(f'    {nid}["{icon} {stage} — {ms}ms"]')

    for a, b in zip(ids, ids[1:]):
        lines.append(f"    {a} --> {b}")

    return "\n".join(lines)
