"""Replay: reconstruct an ExecutionGraph from a JSONL trace file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from egos.core.models import ExecutionGraph, ExecutionNode, NodeStatus


def _iter_lines(source: str | Path) -> Iterator[dict]:
    with open(source) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def replay_graph(source: str | Path, trace_id: str | None = None) -> list[ExecutionGraph]:
    """
    Read a JSONL trace file and return one ExecutionGraph per run_start/run_end pair.
    If trace_id is given, return only that run.
    """
    graphs: dict[str, ExecutionGraph] = {}
    finished: list[ExecutionGraph] = []

    for record in _iter_lines(source):
        event = record.get("event")
        tid = record.get("trace_id", "")

        if trace_id and tid != trace_id:
            continue

        if event == "run_start":
            g = ExecutionGraph(trace_id=tid, goal=record.get("goal", ""))
            graphs[tid] = g

        elif event == "node" and tid in graphs:
            node = ExecutionNode(
                node_id=record.get("node_id", ""),
                trace_id=tid,
                stage=record.get("stage", ""),
                action=record.get("action", ""),
                input=record.get("input", {}),
                output=record.get("output", {}),
                status=NodeStatus(record.get("status", "success")),
                parent_id=record.get("parent_id"),
                timestamp=record.get("timestamp", 0.0),
                duration_ms=record.get("duration_ms", 0.0),
                meta=record.get("meta", {}),
            )
            graphs[tid].nodes.append(node)

        elif event == "run_end" and tid in graphs:
            graphs[tid].finished_at = graphs[tid].started_at + record.get("duration_ms", 0) / 1000
            finished.append(graphs.pop(tid))

    return finished
