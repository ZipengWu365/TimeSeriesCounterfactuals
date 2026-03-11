"""Example: in-process roundtrip against the local MCP server."""

from pathlib import Path

from tscfbench.agent import TSCFBenchMCPServer


def main() -> None:
    server = TSCFBenchMCPServer(repo_root=Path(__file__).resolve().parents[1])
    init = server.handle_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "clientInfo": {"name": "demo", "version": "0.0.1"},
            "capabilities": {},
        },
    })
    print(init)
    tools = server.handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    print(tools)


if __name__ == "__main__":
    main()
