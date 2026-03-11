from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RuntimeProfile:
    id: str
    phase: str
    api_family: str
    model: str
    summary: str
    reasoning_effort: Optional[str] = None
    use_structured_outputs: bool = True
    use_tools: bool = True
    parallel_tool_calls: bool = False
    max_tool_calls: int = 4
    prompt_cache_retention: str = "24h"
    prompt_cache_key: str = "tscfbench"
    use_previous_response_id: bool = True
    allowed_tools: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _planning_profile() -> RuntimeProfile:
    return RuntimeProfile(
        id="openai_responses_planning_research_v1",
        phase="planning",
        api_family="responses",
        model="gpt-5",
        summary="Research planning turn with function tools, structured JSON output, stable tool list, and allowed_tools narrowing.",
        reasoning_effort="medium",
        use_structured_outputs=True,
        use_tools=True,
        parallel_tool_calls=False,
        max_tool_calls=4,
        prompt_cache_retention="24h",
        prompt_cache_key="tscfbench:planning",
        use_previous_response_id=True,
        allowed_tools=[
            "tscf_start_here",
            "tscf_recommend_path",
            "tscf_list_datasets",
            "tscf_list_adapters",
            "tscf_recommend_stack",
            "tscf_plan_context",
            "tscf_repo_map",
            "tscf_list_artifacts",
            "tscf_preview_artifact_table",
            "tscf_read_artifact",
        ],
        notes=[
            "Keep full tool list stable and narrow active tools via allowed_tools.",
            "Use JSON schema outputs for study blueprints and context plans.",
            "Use previous_response_id across retrieval turns, but do not carry full file contents in every turn.",
        ],
    )


def _analysis_profile() -> RuntimeProfile:
    return RuntimeProfile(
        id="openai_responses_analysis_research_v1",
        phase="analysis",
        api_family="responses",
        model="gpt-5",
        summary="Artifact-driven analysis turn with bounded reads, stable cache key, and strict tool subset.",
        reasoning_effort="medium",
        use_structured_outputs=True,
        use_tools=True,
        parallel_tool_calls=False,
        max_tool_calls=6,
        prompt_cache_retention="24h",
        prompt_cache_key="tscfbench:analysis",
        use_previous_response_id=True,
        allowed_tools=[
            "tscf_plan_context",
            "tscf_list_artifacts",
            "tscf_preview_artifact_table",
            "tscf_search_artifact",
            "tscf_read_artifact",
            "tscf_export_runtime_profile",
        ],
        notes=[
            "Prefer reading slices of prediction_frame, metrics, and placebo tables rather than full CSV payloads.",
            "Return machine-readable decisions and next actions for downstream edit turns.",
        ],
    )


def _editing_profile() -> RuntimeProfile:
    return RuntimeProfile(
        id="openai_chat_edit_patch_v1",
        phase="editing",
        api_family="chat_completions",
        model="gpt-4.1",
        summary="Dedicated patch turn for file regeneration with predicted outputs and no tools.",
        reasoning_effort=None,
        use_structured_outputs=False,
        use_tools=False,
        parallel_tool_calls=False,
        max_tool_calls=0,
        prompt_cache_retention="24h",
        prompt_cache_key="tscfbench:editing",
        use_previous_response_id=False,
        allowed_tools=[],
        notes=[
            "Predicted outputs are for file regeneration / small refactors; pass the current file as prediction content.",
            "Do not enable tools in the same request when using predicted outputs.",
            "Keep edit turn separate from retrieval and planning turns.",
        ],
    )


_PROFILES: List[RuntimeProfile] = [_planning_profile(), _analysis_profile(), _editing_profile()]
_PROFILE_ALIASES: Dict[str, str] = {
    "default": "openai_responses_planning_research_v1",
    "planning": "openai_responses_planning_research_v1",
    "analysis": "openai_responses_analysis_research_v1",
    "editing": "openai_chat_edit_patch_v1",
}


def list_runtime_profiles() -> List[RuntimeProfile]:
    return list(_PROFILES)


def runtime_profile_aliases() -> Dict[str, str]:
    return dict(_PROFILE_ALIASES)


def _resolve_profile_id(profile_id: str) -> str:
    key = str(profile_id or "").strip()
    if key in _PROFILE_ALIASES:
        return _PROFILE_ALIASES[key]
    return key


def get_runtime_profile(profile_id: str) -> RuntimeProfile:
    resolved = _resolve_profile_id(profile_id)
    for profile in _PROFILES:
        if profile.id == resolved:
            return profile
    raise KeyError(f"Unknown runtime profile: {profile_id}")


def runtime_profile_catalog() -> List[Dict[str, Any]]:
    alias_inv: Dict[str, List[str]] = {}
    for alias, canonical in _PROFILE_ALIASES.items():
        alias_inv.setdefault(canonical, []).append(alias)
    rows: List[Dict[str, Any]] = []
    for profile in _PROFILES:
        payload = profile.to_dict()
        payload["aliases"] = alias_inv.get(profile.id, [])
        rows.append(payload)
    return rows


def export_runtime_profile(profile_id: str) -> Dict[str, Any]:
    profile = get_runtime_profile(profile_id)
    aliases = [alias for alias, canonical in _PROFILE_ALIASES.items() if canonical == profile.id]
    if profile.api_family == "responses":
        response_format = {
            "type": "json_schema",
            "name": f"{profile.phase}_response",
            "strict": True,
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "actions": {"type": "array", "items": {"type": "string"}},
                    "artifacts_to_read": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "actions", "artifacts_to_read"],
                "additionalProperties": False,
            },
        }
        return {
            "profile": {**profile.to_dict(), "aliases": aliases},
            "request_template": {
                "model": profile.model,
                "input": "<task or user request>",
                "parallel_tool_calls": profile.parallel_tool_calls,
                "max_tool_calls": profile.max_tool_calls,
                "prompt_cache_retention": profile.prompt_cache_retention,
                "prompt_cache_key": profile.prompt_cache_key,
                "metadata": {"runtime_profile": profile.id},
                "text": {"format": response_format},
                "tool_choice": {
                    "type": "allowed_tools",
                    "mode": "auto",
                    "tools": [{"type": "function", "name": name} for name in profile.allowed_tools],
                },
                "previous_response_id": "<previous_response_id>",
            },
        }
    return {
        "profile": {**profile.to_dict(), "aliases": aliases},
        "request_template": {
            "model": profile.model,
            "messages": [
                {"role": "system", "content": "Apply the requested patch and respond only with the updated file content."},
                {"role": "user", "content": "<edit instruction>"},
                {"role": "user", "content": "<current file content>"},
            ],
            "prediction": {"type": "content", "content": "<current file content>"},
            "temperature": 0,
            "metadata": {"runtime_profile": profile.id},
        },
    }


__all__ = [
    "RuntimeProfile",
    "export_runtime_profile",
    "get_runtime_profile",
    "list_runtime_profiles",
    "runtime_profile_aliases",
    "runtime_profile_catalog",
]
