from __future__ import annotations

import json
from typing import Any, Dict, List


def render_agents_md(project_name: str = "tscfbench") -> str:
    lines = [
        f"# AGENTS.md for {project_name}",
        "",
        "## Mission",
        "Keep the project research-first, reproducible, and token-efficient for agentic coding workflows.",
        "",
        "## Operating model",
        "1. Start with structured specs, not long restatements of the task.",
        "2. Use repo maps and context plans before opening large source files or artifacts.",
        "3. Use tools/resources for planning turns; switch to a dedicated edit turn for code regeneration.",
        "4. Prefer minimal diffs and preserve public APIs unless the task explicitly requires a breaking change.",
        "",
        "## Token discipline",
        "- Prefer structured JSON over long prose for machine-machine handoffs.",
        "- Do not inline full CSV tables when a file handle is already available.",
        "- Keep instructions, tool schemas, and common prefixes stable so prompt caching can hit across repeated runs.",
        "- Use `allowed_tools`/tool subsets instead of redefining the full tool list whenever possible.",
        "- For editing, read only the target file or artifact slice you need.",
        "",
        "## Turn separation",
        "- Planning / retrieval turn: use MCP or function tools, structured outputs, repo map, and artifact handles.",
        "- Analysis turn: read bounded slices from metrics, prediction frames, and placebo tables; keep summaries machine-readable.",
        "- Editing turn: disable tools, pass only the patch target plus predicted output / current file when appropriate.",
        "- Reporting turn: summarize from run digests and small table previews, not full artifacts.",
        "",
        "## Research discipline",
        "- Keep seeds fixed in examples and smoke tests.",
        "- Record every benchmark run in run_ledger.jsonl.",
        "- Update dataset cards, adapter catalog, study blueprints, and docs when protocol assumptions change.",
        "- Treat forecasting libraries as forecast-as-counterfactual backends unless causal assumptions are explicitly defended.",
        "",
        "## Preferred commands",
        '- `python -m tscfbench repo-map --query "synthetic control placebo"`',
        "- `python -m tscfbench make-agent-spec -o agent_spec.json`",
        "- `python -m tscfbench make-study-blueprint agent_spec.json -o study_blueprint.json`",
        "- `python -m tscfbench list-adapters`",
        "- `python -m tscfbench export-runtime-profile openai_responses_planning_research_v1 -o runtime_planning.json`",
        "- `python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir`",
        "- `python -m tscfbench plan-context bundle_dir/manifest.json --phase editing --query \"mcp tool registry\"`",
        "- `python -m tscfbench demo`",
        "",
        "## Review gates",
        "Ask for review before deleting datasets, changing benchmark metrics, or widening optional dependencies.",
        "",
        "Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, ChatGPT Apps SDK, Codex, or related docs without me having to explicitly ask.",
    ]
    return "\n".join(lines)


def render_openai_docs_mcp_config(client: str = "vscode") -> Dict[str, Any]:
    client = str(client).lower()
    if client == "cursor":
        return {"mcpServers": {"openaiDeveloperDocs": {"url": "https://developers.openai.com/mcp"}}}
    if client == "codex":
        return {"mcp_servers": {"openaiDeveloperDocs": {"url": "https://developers.openai.com/mcp"}}}
    return {"servers": {"openaiDeveloperDocs": {"type": "http", "url": "https://developers.openai.com/mcp"}}}


def render_local_tscfbench_mcp_config(
    client: str = "vscode",
    *,
    server_name: str = "tscfbench",
    command: str = "tscfbench",
    args: List[str] | None = None,
) -> Dict[str, Any]:
    args = args or ["mcp-server"]
    client = str(client).lower()
    if client == "cursor":
        return {"mcpServers": {server_name: {"command": command, "args": args}}}
    if client == "codex":
        return {"mcp_servers": {server_name: {"command": command, "args": args}}}
    return {"servers": {server_name: {"type": "stdio", "command": command, "args": args}}}


def render_openai_function_calling_example() -> str:
    example = [
        "from openai import OpenAI",
        "from tscfbench.agent.tools import export_openai_function_tools",
        "",
        "client = OpenAI()",
        "tools = export_openai_function_tools(strict=True)",
        "",
        "response = client.responses.create(",
        "    model=\"gpt-5\",",
        "    input=\"Plan a token-efficient analysis turn for the benchmark bundle.\",",
        "    tools=tools,",
        "    tool_choice={",
        "        \"type\": \"allowed_tools\",",
        "        \"mode\": \"auto\",",
        "        \"tools\": [",
        "            {\"type\": \"function\", \"name\": \"tscf_plan_context\"},",
        "            {\"type\": \"function\", \"name\": \"tscf_list_artifacts\"},",
        "            {\"type\": \"function\", \"name\": \"tscf_preview_artifact_table\"},",
        "        ],",
        "    },",
        "    parallel_tool_calls=False,",
        "    prompt_cache_retention=\"24h\",",
        "    prompt_cache_key=\"tscfbench:planning\",",
        ")",
        "",
        "# For editing, switch to a separate no-tools chat-completions turn.",
    ]
    return "\n".join(example)


def render_openai_editing_example() -> str:
    example = [
        "from openai import OpenAI",
        "",
        "client = OpenAI()",
        "current_file = open('src/tscfbench/agent/tools.py', 'r', encoding='utf-8').read()",
        "",
        "response = client.chat.completions.create(",
        "    model=\"gpt-4.1\",",
        "    temperature=0,",
        "    messages=[",
        "        {\"role\": \"system\", \"content\": \"Apply the requested patch and return only the full updated file.\"},",
        "        {\"role\": \"user\", \"content\": \"Add a new tool for list-adapters without changing unrelated code.\"},",
        "        {\"role\": \"user\", \"content\": current_file},",
        "    ],",
        "    prediction={\"type\": \"content\", \"content\": current_file},",
        ")",
    ]
    return "\n".join(example)


def render_json_resource_text(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)
