from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from tscfbench.agent.artifacts import artifact_catalog_text, iter_artifact_refs, summarize_manifest
from tscfbench.agent.runtime_profiles import get_runtime_profile
from tscfbench.agent.tokens import estimate_json_tokens, estimate_text_tokens


_PHASES = {"triage", "analysis", "editing", "report"}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_map_snippet(repo_map_path: Path, query: Optional[str], max_lines: int) -> str:
    text = repo_map_path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not query:
        return "\n".join(lines[:max_lines])

    tokens = [tok.lower() for tok in query.replace("/", " ").replace("_", " ").split() if tok.strip()]
    scored: List[tuple[float, str]] = []
    for line in lines:
        score = 0.0
        ll = line.lower()
        for tok in tokens:
            if tok in ll:
                score += 1.0
            if line.endswith(".py") and tok in ll:
                score += 0.5
        if score > 0:
            scored.append((score, line))
    if not scored:
        return "\n".join(lines[:max_lines])
    scored.sort(key=lambda x: (-x[0], x[1]))
    return "\n".join([line for _, line in scored[:max_lines]])


def _runtime_hints(phase: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    files = manifest.get("files", {})
    profile_key = "runtime_profile_editing" if phase == "editing" else "runtime_profile_planning"
    profile_path = files.get(profile_key)
    profile = None
    if profile_path:
        try:
            profile_payload = _load_json(Path(profile_path))
            profile = profile_payload.get("profile")
        except Exception:  # noqa: BLE001
            profile = None
    if profile is None:
        default_id = "openai_chat_edit_patch_v1" if phase == "editing" else "openai_responses_planning_research_v1"
        profile = get_runtime_profile(default_id).to_dict()
    return {
        "phase": phase,
        "runtime_profile": profile,
        "separate_editing_turn": phase == "editing",
        "prefer_tools_in_turn": bool(profile.get("use_tools")),
        "parallel_tool_calls": bool(profile.get("parallel_tool_calls", False)),
        "prompt_cache_advice": "Keep shared instructions and tool schemas stable across planning/analysis turns; keep editing turns minimal and tool-free when using predicted outputs.",
    }


def build_context_plan(
    manifest_path: str,
    *,
    phase: str = "triage",
    max_tokens: int = 2800,
    query: Optional[str] = None,
    include_repo_map: bool = True,
) -> Dict[str, Any]:
    phase = str(phase).lower().strip()
    if phase not in _PHASES:
        raise ValueError(f"Unknown phase: {phase!r}; expected one of {sorted(_PHASES)}")

    manifest_file = Path(manifest_path)
    manifest = _load_json(manifest_file)

    files = manifest.get("files", {})
    context_pack = _load_json(Path(files["context_pack"]))
    run_digest = _load_json(Path(files["run_digest"]))
    agent_spec = _load_json(Path(files["agent_spec"])) if files.get("agent_spec") else {}
    study_blueprint = _load_json(Path(files["study_blueprint"])) if files.get("study_blueprint") else {}
    repo_map_path = Path(files["repo_map"]) if files.get("repo_map") else None

    blocks: List[Dict[str, Any]] = []
    manifest_summary = summarize_manifest(manifest)
    blocks.append({"kind": "manifest_summary", "priority": 10, "content": manifest_summary, "approx_tokens": estimate_json_tokens(manifest_summary).approx_tokens})

    if agent_spec:
        compact_spec = {
            "task_id": agent_spec.get("task_id"),
            "objective": agent_spec.get("objective"),
            "task_family": agent_spec.get("task_family"),
            "dataset": agent_spec.get("dataset"),
            "model": agent_spec.get("model"),
            "constraints": agent_spec.get("constraints", [])[:4],
            "token_budget": agent_spec.get("token_budget", {}),
        }
        blocks.append({"kind": "agent_spec", "priority": 9 if phase in {"triage", "editing"} else 6, "content": compact_spec, "approx_tokens": estimate_json_tokens(compact_spec).approx_tokens})

    if study_blueprint and phase in {"triage", "analysis"}:
        compact_blueprint = {
            "primary_task": study_blueprint.get("primary_task"),
            "datasets": study_blueprint.get("datasets", [])[:6],
            "top_adapters": [row.get("id") for row in study_blueprint.get("candidate_adapters", [])[:5]],
            "protocol": study_blueprint.get("protocol", {}),
        }
        blocks.append({"kind": "study_blueprint", "priority": 9, "content": compact_blueprint, "approx_tokens": estimate_json_tokens(compact_blueprint).approx_tokens})

    context_summary = {"summary": context_pack.get("summary", {}), "hints": context_pack.get("hints", [])[:4]}
    blocks.append({"kind": "context_summary", "priority": 10, "content": context_summary, "approx_tokens": estimate_json_tokens(context_summary).approx_tokens})

    digest_core = {"dataset_id": run_digest.get("dataset_id"), "model_name": run_digest.get("model_name"), "metrics": run_digest.get("metrics", {}), "next_actions": run_digest.get("next_actions", [])[:4]}
    blocks.append({"kind": "run_digest_core", "priority": 10, "content": digest_core, "approx_tokens": estimate_json_tokens(digest_core).approx_tokens})

    if phase in {"analysis", "report"}:
        preview = {"context_preview": context_pack.get("preview", {}), "run_preview": run_digest.get("preview", {})}
        blocks.append({"kind": "previews", "priority": 8, "content": preview, "approx_tokens": estimate_json_tokens(preview).approx_tokens})

    catalog_text = artifact_catalog_text(manifest)
    blocks.append({"kind": "artifact_catalog", "priority": 7 if phase != "editing" else 6, "content": catalog_text, "approx_tokens": estimate_text_tokens(catalog_text).approx_tokens, "text": True})

    if include_repo_map and repo_map_path is not None and repo_map_path.exists() and phase in {"triage", "analysis", "editing"}:
        repo_text = _repo_map_snippet(repo_map_path, query=query, max_lines=20 if phase == "editing" else 12)
        blocks.append({"kind": "repo_map_snippet", "priority": 9 if phase == "editing" else 5, "content": repo_text, "approx_tokens": estimate_text_tokens(repo_text).approx_tokens, "text": True})

    blocks_sorted = sorted(blocks, key=lambda x: (-x["priority"], x["kind"]))
    selected: List[Dict[str, Any]] = []
    total = 0
    for block in blocks_sorted:
        if total + block["approx_tokens"] > max_tokens and selected:
            continue
        selected.append(block)
        total += block["approx_tokens"]

    omitted = [b["kind"] for b in blocks_sorted if b not in selected]
    refs = [ref.to_dict() for ref in iter_artifact_refs(manifest)]

    plan = {
        "schema_version": "0.5.0",
        "plan_type": "context_window",
        "phase": phase,
        "query": query,
        "max_tokens": int(max_tokens),
        "selected_tokens": int(total),
        "selected_blocks": [{"kind": block["kind"], "approx_tokens": block["approx_tokens"], "content": block["content"]} for block in selected],
        "omitted_blocks": omitted,
        "artifact_refs": refs,
        "runtime_hints": _runtime_hints(phase, manifest),
        "routing_hints": [
            "Prefer reading specific artifact slices instead of loading full CSV files.",
            "Keep JSON specs stable and edit them directly for prompt-cache friendly iteration.",
            "Use repo map snippets for code navigation; only open full source files when a specific patch target is identified.",
        ],
    }
    plan["token_estimate"] = estimate_json_tokens(plan).to_dict()
    return plan
