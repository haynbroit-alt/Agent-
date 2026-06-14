"""Tool registry: register, discover, and invoke EGOS tools."""
from __future__ import annotations

import os
import subprocess
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Base class for all EGOS tools."""

    name: str = ""
    description: str = ""
    keywords: list[str] = []

    @abstractmethod
    def run(self, **kwargs: Any) -> Any: ...


class EchoTool(BaseTool):
    name = "echo"
    description = "Return text as-is (default fallback tool)"
    keywords = []

    def run(self, text: str = "", **_: Any) -> str:
        return text


class ShellTool(BaseTool):
    name = "shell"
    description = "Run a safe shell command and return stdout"
    keywords = ["run", "execute", "list", "show", "find", "ls", "cat", "grep"]

    # Only these binaries are permitted
    _ALLOWED_CMDS = frozenset({"ls", "cat", "echo", "pwd", "find", "grep", "wc", "head", "tail", "date", "uname"})

    def run(self, query: str = "", command: str = "", **_: Any) -> str:
        cmd = command or query
        binary = cmd.strip().split()[0] if cmd.strip() else ""
        if binary not in self._ALLOWED_CMDS:
            raise PermissionError(f"shell: '{binary}' is not in the allowed command list")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10  # noqa: S602
        )
        return result.stdout.strip() or result.stderr.strip()


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read a local file and return its content"
    keywords = ["read", "open", "load", "get file", "show file"]

    def run(self, path: str = "", query: str = "", **_: Any) -> str:
        target = path or query
        if not os.path.isfile(target):
            raise FileNotFoundError(f"read_file: '{target}' not found")
        with open(target) as f:
            return f.read(8192)


class ToolRegistry:
    """Holds all registered tools; thread-safe for reads."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> "ToolRegistry":
        self._tools[tool.name] = tool
        return self

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    @classmethod
    def default(cls) -> "ToolRegistry":
        """Return a registry pre-loaded with built-in tools."""
        r = cls()
        r.register(EchoTool())
        r.register(ShellTool())
        r.register(ReadFileTool())
        return r
