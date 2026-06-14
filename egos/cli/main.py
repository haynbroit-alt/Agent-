"""EGOS CLI — egos run / egos trace / egos graph."""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from egos.core.runtime import Runtime
from egos.graph.visualizer import render_ascii, render_mermaid
from egos.trace.logger import TraceLogger
from egos.trace.replay import replay_graph


def cmd_run(args: argparse.Namespace) -> int:
    """egos run <goal> [--out trace.jsonl] [--quiet]"""
    goal = " ".join(args.goal)
    if not goal.strip():
        print("error: goal cannot be empty", file=sys.stderr)
        return 1

    logger: TraceLogger
    if args.out:
        logger = TraceLogger(output=args.out)
    elif args.quiet:
        logger = TraceLogger(silent=True)
    else:
        logger = TraceLogger()

    with logger:
        runtime = Runtime(logger=logger)
        graph = runtime.run(goal)

    if not args.quiet:
        print("", file=sys.stderr)
        print(render_ascii(graph), file=sys.stderr)

    return 0 if graph.success else 1


def cmd_trace(args: argparse.Namespace) -> int:
    """egos trace <file.jsonl> [--trace-id ID] [--pretty]"""
    source = Path(args.file)
    if not source.exists():
        print(f"error: '{source}' not found", file=sys.stderr)
        return 1

    graphs = replay_graph(source, trace_id=args.trace_id or None)
    if not graphs:
        print("No runs found.", file=sys.stderr)
        return 1

    for g in graphs:
        if args.pretty:
            print(json.dumps(g.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(json.dumps(g.to_dict(), ensure_ascii=False))
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    """egos graph <goal> [--format ascii|mermaid]"""
    goal = " ".join(args.goal)
    buf = io.StringIO()
    logger = TraceLogger(output=buf)
    with logger:
        runtime = Runtime(logger=logger)
        graph = runtime.run(goal)

    fmt = args.format or "ascii"
    if fmt == "mermaid":
        print(render_mermaid(graph))
    else:
        print(render_ascii(graph))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="egos", description="EGOS — Execution Graph OS")
    sub = p.add_subparsers(dest="command", required=True)

    # egos run
    run_p = sub.add_parser("run", help="Execute a goal and emit a JSONL trace")
    run_p.add_argument("goal", nargs="+", help="Natural language goal")
    run_p.add_argument("--out", metavar="FILE", help="Write trace to JSONL file")
    run_p.add_argument("--quiet", action="store_true", help="Suppress output")
    run_p.set_defaults(func=cmd_run)

    # egos trace
    trace_p = sub.add_parser("trace", help="Inspect a JSONL trace file")
    trace_p.add_argument("file", help="Path to trace.jsonl")
    trace_p.add_argument("--trace-id", metavar="ID", help="Filter by trace ID")
    trace_p.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    trace_p.set_defaults(func=cmd_trace)

    # egos graph
    graph_p = sub.add_parser("graph", help="Visualize execution as a graph")
    graph_p.add_argument("goal", nargs="+", help="Natural language goal")
    graph_p.add_argument("--format", choices=["ascii", "mermaid"], default="ascii")
    graph_p.set_defaults(func=cmd_graph)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
