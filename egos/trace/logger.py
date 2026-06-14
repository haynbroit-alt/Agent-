"""JSONL trace logger: every node gets a line, every run gets a header + footer."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import IO, Any

from egos.core.models import ExecutionGraph, ExecutionNode


class TraceLogger:
    """
    Writes structured JSONL traces.

    - stdout by default (pipe-friendly)
    - pass a file path or IO object to persist to disk
    - silent=True suppresses all output (useful in tests)
    """

    def __init__(
        self,
        output: str | Path | IO[str] | None = None,
        silent: bool = False,
    ) -> None:
        self._silent = silent
        self._file: IO[str] | None = None
        self._owns_file = False

        if isinstance(output, (str, Path)):
            self._file = open(output, "a")  # noqa: SIM115
            self._owns_file = True
        elif output is not None:
            self._file = output
        # if None: use sys.stdout lazily

    def _write(self, record: dict[str, Any]) -> None:
        if self._silent:
            return
        line = json.dumps(record, ensure_ascii=False)
        dest = self._file or sys.stdout
        dest.write(line + "\n")
        if hasattr(dest, "flush"):
            dest.flush()

    def begin(self, graph: ExecutionGraph) -> None:
        self._write({"event": "run_start", "trace_id": graph.trace_id, "goal": graph.goal})

    def node(self, node: ExecutionNode) -> None:
        self._write({"event": "node", **node.to_dict()})

    def end(self, graph: ExecutionGraph) -> None:
        self._write({
            "event": "run_end",
            "trace_id": graph.trace_id,
            "success": graph.success,
            "duration_ms": graph.duration_ms,
            "nodes": len(graph.nodes),
        })

    def close(self) -> None:
        if self._owns_file and self._file:
            self._file.close()
            self._file = None

    def __enter__(self) -> "TraceLogger":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
