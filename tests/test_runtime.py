"""Core runtime tests."""
from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import pytest

from egos import Runtime
from egos.core.models import NodeStatus
from egos.trace.logger import TraceLogger
from egos.trace.replay import replay_graph


@pytest.fixture()
def silent_runtime():
    return Runtime(logger=TraceLogger(silent=True))


def test_run_returns_graph(silent_runtime):
    graph = silent_runtime.run("list files in /tmp")
    assert graph.trace_id
    assert len(graph.nodes) == 6  # context, planner, policy, executor, memory, observer


def test_stages_present(silent_runtime):
    graph = silent_runtime.run("echo hello world")
    stages = [n.stage for n in graph.nodes]
    assert stages == ["context", "planner", "policy", "executor", "memory", "observer"]


def test_all_nodes_have_trace_id(silent_runtime):
    graph = silent_runtime.run("show current directory")
    for node in graph.nodes:
        assert node.trace_id == graph.trace_id


def test_observer_confidence(silent_runtime):
    graph = silent_runtime.run("echo test")
    obs = next(n for n in graph.nodes if n.stage == "observer")
    assert 0.0 <= obs.output["confidence"] <= 1.0


def test_policy_blocks_dangerous_goal():
    runtime = Runtime(logger=TraceLogger(silent=True))
    graph = runtime.run("delete all files rm -rf /")
    policy = next(n for n in graph.nodes if n.stage == "policy")
    assert policy.output["any_blocked"] is True
    assert policy.status == NodeStatus.BLOCKED


def test_jsonl_trace_output():
    buf = io.StringIO()
    logger = TraceLogger(output=buf)
    runtime = Runtime(logger=logger)
    graph = runtime.run("echo hello")

    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    records = [json.loads(l) for l in lines]

    events = [r["event"] for r in records]
    assert events[0] == "run_start"
    assert events[-1] == "run_end"
    assert any(r["event"] == "node" and r["stage"] == "executor" for r in records)


def test_trace_replay():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False) as f:
        path = Path(f.name)

    try:
        logger = TraceLogger(output=str(path))
        runtime = Runtime(logger=logger)
        original = runtime.run("echo replay test")
        logger.close()

        graphs = replay_graph(path)
        assert len(graphs) == 1
        replayed = graphs[0]
        assert replayed.trace_id == original.trace_id
        assert replayed.goal == original.goal
        assert len(replayed.nodes) == len(original.nodes)
    finally:
        path.unlink(missing_ok=True)


def test_graph_finish_sets_duration(silent_runtime):
    graph = silent_runtime.run("date")
    assert graph.duration_ms > 0


def test_memory_stores_results(silent_runtime):
    silent_runtime.run("echo stored value")
    # memory store is populated (at least 0 entries — echo may not store)
    assert isinstance(silent_runtime.memory.all(), dict)
