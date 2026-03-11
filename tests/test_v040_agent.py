import json
from pathlib import Path

from tscfbench.agent import (
    AgentResearchTaskSpec,
    TSCFBenchMCPServer,
    TokenBudget,
    build_context_plan,
    build_panel_agent_bundle,
    export_openai_function_tools,
    invoke_tool,
    list_artifacts,
    preview_tabular_artifact,
    read_text_artifact,
    render_local_tscfbench_mcp_config,
)


def _make_bundle(tmp_path: Path):
    spec = AgentResearchTaskSpec(
        dataset="synthetic_latent_factor",
        model="simple_scm",
        seed=3,
        intervention_t=45,
        n_units=8,
        n_periods=80,
        max_time_placebos=4,
        token_budget=TokenBudget(input_limit=3200, reserve_for_output=600, reserve_for_instructions=500),
    )
    return build_panel_agent_bundle(spec, output_dir=tmp_path / "bundle", include_repo_map=True, repo_root=Path(__file__).resolve().parents[1])


def test_context_plan_smoke(tmp_path: Path):
    bundle = _make_bundle(tmp_path)
    plan = build_context_plan(bundle.manifest_path, phase="editing", max_tokens=1800, query="mcp tool registry")
    assert plan["phase"] == "editing"
    assert plan["selected_tokens"] <= 1800 or len(plan["selected_blocks"]) == 1
    assert plan["runtime_hints"]["separate_editing_turn"] is True


def test_artifact_read_preview_smoke(tmp_path: Path):
    bundle = _make_bundle(tmp_path)
    artifacts = list_artifacts(bundle.manifest_path)
    assert len(artifacts) > 0
    preview = preview_tabular_artifact(bundle.manifest_path, kind="prediction_frame", rows=3)
    assert preview["rows_returned"] == 3
    snippet = read_text_artifact(bundle.manifest_path, kind="metrics", max_chars=120)
    assert snippet["returned_chars"] > 0


def test_openai_tool_export_smoke():
    tools = export_openai_function_tools(strict=True)
    names = {tool["name"] for tool in tools}
    assert "tscf_plan_context" in names
    first = tools[0]
    assert first["type"] == "function"
    assert first["strict"] is True


def test_invoke_tool_smoke(tmp_path: Path):
    bundle = _make_bundle(tmp_path)
    out = invoke_tool("tscf_plan_context", {"manifest_path": bundle.manifest_path, "phase": "analysis", "max_tokens": 2000}, repo_root=Path(__file__).resolve().parents[1])
    assert out["phase"] == "analysis"
    assert out["max_tokens"] == 2000


def test_local_mcp_config_smoke():
    cfg = render_local_tscfbench_mcp_config("vscode")
    assert cfg["servers"]["tscfbench"]["type"] == "stdio"


def test_mcp_server_roundtrip_smoke(tmp_path: Path):
    bundle = _make_bundle(tmp_path)
    server = TSCFBenchMCPServer(repo_root=Path(__file__).resolve().parents[1])
    init = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "clientInfo": {"name": "pytest", "version": "0.0.1"},
                "capabilities": {},
            },
        }
    )
    assert init[0]["result"]["protocolVersion"] == "2025-11-25"

    tools_list = server.handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert any(tool["name"] == "tscf_plan_context" for tool in tools_list[0]["result"]["tools"])

    call = server.handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "tscf_plan_context",
                "arguments": {"manifest_path": bundle.manifest_path, "phase": "triage", "max_tokens": 1800},
            },
        }
    )
    assert call[0]["result"]["isError"] is False
    assert call[0]["result"]["structuredContent"]["phase"] == "triage"

    resources = server.handle_message({"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}})
    assert any(item["uri"].startswith("tscfbench://") for item in resources[0]["result"]["resources"])

    prompt = server.handle_message(
        {"jsonrpc": "2.0", "id": 5, "method": "prompts/get", "params": {"name": "bundle-triage", "arguments": {"manifest_path": bundle.manifest_path}}}
    )
    assert prompt[0]["result"]["messages"][0]["content"]["type"] == "text"
