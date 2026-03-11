from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import json

from tscfbench.agent.runtime_profiles import get_runtime_profile
from tscfbench.agent.specs import AgentResearchTaskSpec
from tscfbench.integrations.cards import adapter_catalog, group_install_profiles, recommend_adapter_stack


@dataclass(frozen=True)
class ResearchStudyBlueprint:
    schema_version: str
    study_type: str
    objective: str
    primary_task: str
    datasets: List[str]
    candidate_adapters: List[Dict[str, Any]]
    protocol: Dict[str, Any]
    install_profiles: Dict[str, List[str]]
    runtime_profiles: Dict[str, Any]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: Union[str, Path], pretty: bool = True) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2 if pretty else None, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )


def build_research_study_blueprint(spec: AgentResearchTaskSpec, *, max_adapters: int = 8) -> ResearchStudyBlueprint:
    task = getattr(spec, "task_family", "panel") or "panel"
    datasets = list(getattr(spec, "dataset_suite", []) or [spec.dataset])
    planning_profile_id = getattr(spec, "planning_runtime_profile", "openai_responses_planning_research_v1")
    editing_profile_id = getattr(spec, "editing_runtime_profile", "openai_chat_edit_patch_v1")

    protocol = {
        "metrics": [
            "pre_rmspe",
            "post_rmspe",
            "post_pre_rmspe_ratio",
            "avg_effect",
            "cum_effect",
        ],
        "placebo_protocol": {
            "space_placebo": True,
            "time_placebo": True,
            "placebo_pre_rmspe_factor": spec.placebo_pre_rmspe_factor,
            "min_pre_periods": spec.min_pre_periods,
            "max_time_placebos": spec.max_time_placebos,
        },
        "reporting": {
            "summary_artifacts": ["context_pack.json", "run_digest.json", "panel_report.md"],
            "load_large_tables_by_handle": True,
            "preferred_output_mode": "structured_json_then_markdown",
        },
    }
    notes = [
        "Start with built-in baselines for reproducibility, then widen to external adapters.",
        "Treat forecast-based approaches as auxiliary counterfactual generators, not default causal baselines.",
        "Keep the planning turn tool-enabled and the editing turn tool-free for patch generation.",
    ]
    return ResearchStudyBlueprint(
        schema_version="0.5.0",
        study_type="research_blueprint",
        objective=spec.objective,
        primary_task=task,
        datasets=datasets,
        candidate_adapters=recommend_adapter_stack(task_family=task, goal="research", token_aware=True, max_adapters=max_adapters),
        protocol=protocol,
        install_profiles=group_install_profiles(),
        runtime_profiles={
            "planning": get_runtime_profile(planning_profile_id).to_dict(),
            "editing": get_runtime_profile(editing_profile_id).to_dict(),
        },
        notes=notes,
    )


__all__ = ["ResearchStudyBlueprint", "build_research_study_blueprint"]
