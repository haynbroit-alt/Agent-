# EGOS — Execution Graph OS

> **AI agents that act, trace, and learn — not just generate text.**

EGOS is an open-source Python runtime that turns every agent decision into a **traceable, replayable execution graph**. Every step is logged, every policy gate is auditable, every run can be replayed from a JSONL file.

```
$ egos run "list files in /tmp"

{"event":"run_start","trace_id":"a3f8c12d9e01","goal":"list files in /tmp"}
{"event":"node","stage":"context","action":"parse_intent","status":"success","duration_ms":0.1}
{"event":"node","stage":"planner","action":"decompose","status":"success","duration_ms":0.2}
{"event":"node","stage":"policy","action":"evaluate","status":"success","duration_ms":0.1}
{"event":"node","stage":"executor","action":"run_steps","status":"success","duration_ms":8.4}
{"event":"node","stage":"memory","action":"store","status":"success","duration_ms":0.1}
{"event":"node","stage":"observer","action":"evaluate","status":"success","duration_ms":0.1}
{"event":"run_end","trace_id":"a3f8c12d9e01","success":true,"duration_ms":9.1}

  trace: a3f8c12d9e01  goal: list files in /tmp

  [✓] CONTEXT       0.1ms
        │
  [✓] PLANNER       0.2ms
        │
  [✓] POLICY        0.1ms
        │
  [✓] EXECUTOR      8.4ms
        │
  [✓] MEMORY        0.1ms
        │
  [✓] OBSERVER      0.1ms

  ► SUCCESS  total=9.1ms  nodes=6
```

---

## Why EGOS?

Most agent frameworks give you a black box. EGOS gives you a **graph**.

| | Traditional agent | EGOS |
|---|---|---|
| Decisions | Hidden | Traced node-by-node |
| Errors | Opaque stack traces | Pinpointed to stage |
| Replay | Impossible | `egos trace run.jsonl` |
| Policy | Ad-hoc | Explicit gate before every execution |
| Learning | Prompt tweaking | Structured JSONL — ML-ready |

---

## The Execution Loop

Every EGOS run follows the same six-stage pipeline:

```
Context → Planner → Policy → Executor → Memory → Observer
```

| Stage | What it does |
|---|---|
| **Context** | Parses intent from the user goal |
| **Planner** | Decomposes goal into ordered tool steps |
| **Policy** | Safety gate — allow or block each step |
| **Executor** | Runs approved steps via the tool registry |
| **Memory** | Persists results for future context |
| **Observer** | Scores the run, emits confidence |

Each stage emits one `ExecutionNode` → the full chain is an `ExecutionGraph`.

---

## Install

```bash
pip install egos          # once published to PyPI
```

or from source:

```bash
git clone https://github.com/haynbroit-alt/agent-
cd agent-
pip install -e ".[dev]"
```

---

## CLI

```bash
# Run a goal — trace goes to stdout by default
egos run "show current date"

# Save trace to a file
egos run "list files in /tmp" --out run.jsonl

# Inspect a saved trace
egos trace run.jsonl --pretty

# Visualize as ASCII graph
egos graph "echo hello world"

# Visualize as Mermaid (paste into mermaid.live)
egos graph "echo hello world" --format mermaid
```

---

## Python API

```python
from egos import Runtime
from egos.trace.logger import TraceLogger

# Default: trace to stdout
runtime = Runtime()
graph = runtime.run("list files in /tmp")

print(graph.trace_id)       # "a3f8c12d9e01"
print(graph.success)        # True
print(graph.duration_ms)    # 9.1

# Inspect stages
for node in graph.nodes:
    print(f"[{node.stage}] {node.status.value} — {node.duration_ms:.1f}ms")

# Persist trace to file
with TraceLogger("run.jsonl") as logger:
    runtime = Runtime(logger=logger)
    graph = runtime.run("find all Python files")
```

---

## Custom Tools

```python
from egos.tools.registry import BaseTool, ToolRegistry
from egos import Runtime

class WeatherTool(BaseTool):
    name = "weather"
    description = "Get current weather for a city"
    keywords = ["weather", "temperature", "forecast"]

    def run(self, query: str = "", **_) -> str:
        return f"Sunny, 22°C in {query}"  # replace with real API call

registry = ToolRegistry.default()
registry.register(WeatherTool())

runtime = Runtime(registry=registry)
graph = runtime.run("weather in Paris")
```

---

## Trace Format (JSONL)

Every line is a valid JSON object. Three event types:

```jsonc
// Run start
{"event": "run_start", "trace_id": "a3f8c12d9e01", "goal": "list files in /tmp"}

// Execution node
{
  "event": "node",
  "node_id": "f3a9b2c1",
  "trace_id": "a3f8c12d9e01",
  "stage": "executor",
  "action": "run_steps",
  "input": {"steps_count": 1},
  "output": {"results": [{"tool": "shell", "status": "ok", "output": "file1\nfile2"}]},
  "status": "success",
  "parent_id": "9e1d4f72",
  "timestamp": 1718361408.42,
  "duration_ms": 8.4,
  "meta": {}
}

// Run end
{"event": "run_end", "trace_id": "a3f8c12d9e01", "success": true, "duration_ms": 9.1, "nodes": 6}
```

This format is:
- **Streamable** — parse line by line
- **ML-ready** — load with pandas, DuckDB, or any JSONL reader
- **Replayable** — `egos trace run.jsonl` reconstructs the full graph

---

## Replay

```python
from egos.trace.replay import replay_graph

graphs = replay_graph("run.jsonl")
for g in graphs:
    print(g.trace_id, g.success, g.duration_ms)
    for node in g.nodes:
        print(f"  [{node.stage}] {node.status.value}")
```

---

## Built-in Tools

| Tool | Description | Allowed commands |
|---|---|---|
| `echo` | Returns text as-is | — |
| `shell` | Runs safe shell commands | `ls cat echo pwd find grep wc head tail date uname` |
| `read_file` | Reads a local file (max 8KB) | — |

All other binaries are blocked at the tool level. The `policy` stage adds a second layer for goal-level filtering.

---

## Policy

The policy stage runs **before** the executor. It blocks:

- Tools in the denied list (`rm_rf`, `drop_db`, `format_disk`, …)
- Goals containing dangerous patterns (`rm -rf`, `delete all`, `drop table`, …)

Blocked steps produce `NodeStatus.BLOCKED` nodes — they appear in the trace and graph but are never executed.

```python
graph = runtime.run("delete all files rm -rf /")
policy = next(n for n in graph.nodes if n.stage == "policy")
print(policy.output["any_blocked"])  # True
print(policy.status)                 # NodeStatus.BLOCKED
```

---

## Tests

```bash
pytest
# or with coverage
pytest --cov=egos
```

---

## Roadmap

- [ ] LLM planner (OpenRouter / Anthropic) — swap heuristic with model tool-call
- [ ] Async runtime (`arun()`)
- [ ] Persistent memory backend (SQLite, Redis)
- [ ] Web UI trace viewer
- [ ] Multi-agent orchestration (sub-graphs)
- [ ] OpenTelemetry export

---

## License

MIT — see [LICENSE](LICENSE).

---

## Project Structure

```
egos/
├── core/
│   ├── models.py      # ExecutionNode, ExecutionGraph, NodeStatus
│   ├── runtime.py     # Main execution loop
│   ├── context.py     # Stage 1: intent parsing
│   ├── planner.py     # Stage 2: step decomposition
│   ├── policy.py      # Stage 3: safety gate
│   ├── executor.py    # Stage 4: tool execution
│   ├── memory.py      # Stage 5: result persistence
│   └── observer.py    # Stage 6: confidence scoring
├── trace/
│   ├── logger.py      # JSONL trace writer
│   └── replay.py      # Trace reconstruction
├── graph/
│   └── visualizer.py  # ASCII + Mermaid output
├── tools/
│   └── registry.py    # Tool registration + built-ins
└── cli/
    └── main.py        # egos run / trace / graph
```

---

*EGOS: from black-box agent to observable execution graph.*
