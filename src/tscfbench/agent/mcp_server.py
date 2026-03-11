from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from tscfbench import __version__
from tscfbench.agent.runtime_profiles import runtime_profile_catalog
from tscfbench.agent.specs import AgentResearchTaskSpec
from tscfbench.agent.templates import (
    render_agents_md,
    render_json_resource_text,
    render_local_tscfbench_mcp_config,
    render_openai_docs_mcp_config,
    render_openai_editing_example,
    render_openai_function_calling_example,
)
from tscfbench.agent.tools import get_tool_registry, invoke_tool
from tscfbench.integrations.cards import adapter_catalog


_PROTOCOL_VERSION = "2025-11-25"


@dataclass(frozen=True)
class ResourceSpec:
    uri: str
    name: str
    title: str
    description: str
    mime_type: str
    text: str

    def list_item(self) -> Dict[str, Any]:
        return {"uri": self.uri, "name": self.name, "title": self.title, "description": self.description, "mimeType": self.mime_type}

    def read_item(self) -> Dict[str, Any]:
        return {"uri": self.uri, "mimeType": self.mime_type, "text": self.text}


@dataclass(frozen=True)
class PromptSpec:
    name: str
    title: str
    description: str
    arguments: List[Dict[str, Any]]

    def list_item(self) -> Dict[str, Any]:
        return {"name": self.name, "title": self.title, "description": self.description, "arguments": self.arguments}


def _panel_experiment_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PanelExperimentSpec",
        "type": "object",
        "required": ["dataset", "model", "seed", "intervention_t", "n_units", "n_periods", "placebo_pre_rmspe_factor", "min_pre_periods", "max_time_placebos"],
        "properties": {
            "dataset": {"type": "string"},
            "model": {"type": "string"},
            "seed": {"type": "integer"},
            "intervention_t": {"type": "integer"},
            "n_units": {"type": "integer"},
            "n_periods": {"type": "integer"},
            "placebo_pre_rmspe_factor": {"type": "number"},
            "min_pre_periods": {"type": "integer"},
            "max_time_placebos": {"type": "integer"},
        },
        "additionalProperties": False,
    }


def _resources() -> List[ResourceSpec]:
    return [
        ResourceSpec("tscfbench://schemas/agent_research_task_spec.json", "agent_research_task_spec", "AgentResearchTaskSpec schema", "Compact JSON spec for token-efficient research runs.", "application/json", render_json_resource_text(AgentResearchTaskSpec.json_schema())),
        ResourceSpec("tscfbench://schemas/panel_experiment_spec.json", "panel_experiment_spec", "PanelExperimentSpec schema", "Panel benchmark experiment schema.", "application/json", render_json_resource_text(_panel_experiment_schema())),
        ResourceSpec("tscfbench://catalogs/adapter_catalog.json", "adapter_catalog", "Adapter catalog", "Built-in and optional adapter registry with install hints and availability.", "application/json", render_json_resource_text(adapter_catalog(include_availability=True))),
        ResourceSpec("tscfbench://catalogs/runtime_profiles.json", "runtime_profiles", "Runtime profiles", "Planning / analysis / editing runtime profiles for API or editor agents.", "application/json", render_json_resource_text(runtime_profile_catalog())),
        ResourceSpec("tscfbench://templates/AGENTS.md", "agents_md_template", "AGENTS.md template", "Template for agent-facing repository rules.", "text/markdown", render_agents_md()),
        ResourceSpec("tscfbench://templates/vscode_mcp.json", "vscode_mcp_template", "VS Code MCP config", "Local stdio MCP config for VS Code Agent Mode.", "application/json", render_json_resource_text(render_local_tscfbench_mcp_config("vscode"))),
        ResourceSpec("tscfbench://templates/cursor_mcp.json", "cursor_mcp_template", "Cursor MCP config", "Local stdio MCP config for Cursor.", "application/json", render_json_resource_text(render_local_tscfbench_mcp_config("cursor"))),
        ResourceSpec("tscfbench://templates/openai_docs_mcp.json", "openai_docs_mcp_template", "OpenAI Docs MCP config", "OpenAI developer docs MCP template.", "application/json", render_json_resource_text(render_openai_docs_mcp_config("vscode"))),
        ResourceSpec("tscfbench://examples/openai_function_calling.py", "openai_function_calling_example", "OpenAI planning example", "Example showing how to use exported function tools with Responses API.", "text/x-python", render_openai_function_calling_example()),
        ResourceSpec("tscfbench://examples/openai_editing.py", "openai_editing_example", "OpenAI editing example", "Example showing how to run a separate predicted-output editing turn.", "text/x-python", render_openai_editing_example()),
    ]


_PROMPTS = [
    PromptSpec("bundle-triage", "Bundle triage", "Summarize a benchmark bundle and decide the next read-on-demand actions.", [{"name": "manifest_path", "description": "Path to manifest.json", "required": True}, {"name": "question", "description": "Optional user question", "required": False}]),
    PromptSpec("minimal-patch-plan", "Minimal patch plan", "Plan the smallest patch that satisfies a coding change request.", [{"name": "task", "description": "The requested coding change", "required": True}, {"name": "focus_query", "description": "Repo-map query terms", "required": False}]),
    PromptSpec("study-blueprint", "Study blueprint", "Draft a compact research study blueprint using adapters, runtime profiles, and datasets.", [{"name": "objective", "description": "Research objective", "required": True}, {"name": "task_family", "description": "Task family such as panel or impact", "required": False}]),
]


def _prompt_messages(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "bundle-triage":
        manifest_path = arguments.get("manifest_path", "manifest.json")
        question = arguments.get("question") or "Summarize the run and identify the smallest next artifact reads needed."
        text = f"Read the bundle at `{manifest_path}` using context planning and artifact handles. First summarize the benchmark state, then answer: {question} Prefer compact JSON and bounded artifact slices over loading whole files."
    elif name == "minimal-patch-plan":
        task = arguments.get("task", "Describe the change.")
        focus_query = arguments.get("focus_query") or "repo map"
        text = f"Plan the smallest viable patch for this task: {task}. Start with repo-map query `{focus_query}` and keep the edit turn separate from retrieval turns."
    elif name == "study-blueprint":
        objective = arguments.get("objective", "Design a research-grade study.")
        task_family = arguments.get("task_family") or "panel"
        text = f"Draft a compact study blueprint for task family `{task_family}` with objective: {objective}. Prefer adapter cards, dataset suites, runtime profiles, and JSON-first deliverables."
    else:
        raise KeyError(f"Unknown prompt: {name}")
    return {"description": text, "messages": [{"role": "user", "content": {"type": "text", "text": text}}]}


class TSCFBenchMCPServer:
    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root or ".").resolve()
        self.tools = get_tool_registry()
        self.resources = {res.uri: res for res in _resources()}
        self.prompts = {p.name: p for p in _PROMPTS}

    def _response(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _error(self, request_id: Any, code: int, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
        err: Dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": err}

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params") or {}

        if method == "initialize":
            return self._response(request_id, {"protocolVersion": _PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}, "prompts": {"listChanged": False}}, "serverInfo": {"name": "tscfbench", "title": "tscfbench MCP", "version": __version__, "description": "Time-series counterfactual benchmark tools, resources, and prompts for agent-native research workflows."}, "instructions": "Prefer token-bounded context plans, artifact handles, study blueprints, and minimal diffs. Split retrieval turns from editing turns."})
        if method == "ping":
            return self._response(request_id, {})
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return self._response(request_id, {"tools": [tool.to_mcp_tool() for tool in self.tools.values()]})
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if name not in self.tools:
                return self._error(request_id, -32602, f"Unknown tool: {name}")
            try:
                result = invoke_tool(str(name), arguments, repo_root=self.repo_root)
                text = json.dumps(result, ensure_ascii=False, sort_keys=True)
                return self._response(request_id, {"content": [{"type": "text", "text": text}], "structuredContent": result, "isError": False})
            except Exception as exc:  # noqa: BLE001
                return self._response(request_id, {"content": [{"type": "text", "text": str(exc)}], "structuredContent": {"error": str(exc)}, "isError": True})
        if method == "resources/list":
            return self._response(request_id, {"resources": [res.list_item() for res in self.resources.values()]})
        if method == "resources/read":
            uri = params.get("uri")
            if uri not in self.resources:
                return self._error(request_id, -32602, f"Unknown resource: {uri}")
            return self._response(request_id, {"contents": [self.resources[str(uri)].read_item()]})
        if method == "prompts/list":
            return self._response(request_id, {"prompts": [p.list_item() for p in self.prompts.values()]})
        if method == "prompts/get":
            name = params.get("name")
            if name not in self.prompts:
                return self._error(request_id, -32602, f"Unknown prompt: {name}")
            args = params.get("arguments") or {}
            try:
                return self._response(request_id, _prompt_messages(str(name), args))
            except Exception as exc:  # noqa: BLE001
                return self._error(request_id, -32602, str(exc))
        return self._error(request_id, -32601, f"Method not found: {method}")

    def handle_message(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            responses: List[Dict[str, Any]] = []
            for item in payload:
                if not isinstance(item, dict):
                    responses.append(self._error(None, -32600, "Invalid Request"))
                    continue
                resp = self.handle_request(item)
                if resp is not None and item.get("id") is not None:
                    responses.append(resp)
            return responses
        if not isinstance(payload, dict):
            return [self._error(None, -32600, "Invalid Request")]
        resp = self.handle_request(payload)
        if resp is None or payload.get("id") is None:
            return []
        return [resp]


def _iter_stdin_lines() -> List[str]:
    return [line for line in sys.stdin]


def main() -> int:
    server = TSCFBenchMCPServer(repo_root=Path.cwd())
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}) + "\n")
            sys.stdout.flush()
            continue
        for resp in server.handle_message(payload):
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0
