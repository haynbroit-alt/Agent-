"""Tool registry tests."""
from __future__ import annotations

import pytest

from egos.tools.registry import EchoTool, ShellTool, ToolRegistry


def test_echo_tool():
    t = EchoTool()
    assert t.run(text="hello") == "hello"


def test_shell_tool_allowed():
    t = ShellTool()
    result = t.run(command="echo egos")
    assert "egos" in result


def test_shell_tool_blocked():
    t = ShellTool()
    with pytest.raises(PermissionError):
        t.run(command="rm -rf /tmp/x")


def test_registry_default():
    r = ToolRegistry.default()
    assert "echo" in r.list_tools()
    assert "shell" in r.list_tools()
    assert "read_file" in r.list_tools()


def test_registry_custom_tool():
    from egos.tools.registry import BaseTool

    class PingTool(BaseTool):
        name = "ping"
        description = "pong"
        keywords = ["ping"]

        def run(self, **_):
            return "pong"

    r = ToolRegistry()
    r.register(PingTool())
    assert r.get("ping").run() == "pong"
