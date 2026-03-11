from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

from tscfbench.agent.tokens import TokenBudget
from tscfbench.experiments import PanelExperimentSpec


@dataclass(frozen=True)
class AgentResearchTaskSpec:
    """Compact, schema-stable experiment spec for agent-driven benchmark work."""

    task_id: str = "panel_counterfactual_research"
    objective: str = "Run a research-grade panel counterfactual benchmark and return concise, machine-readable artifacts."
    task_family: str = "panel"
    research_track: str = "scientific_discovery"
    dataset: str = "synthetic_latent_factor"
    dataset_suite: List[str] = field(
        default_factory=lambda: [
            "synthetic_latent_factor",
            "german_reunification",
            "california_prop99",
            "basque_country",
        ]
    )
    model: str = "simple_scm"
    candidate_adapters: List[str] = field(
        default_factory=lambda: [
            "simple_scm_builtin",
            "did_builtin",
            "pysyncon",
            "scpi",
            "tfp_causalimpact",
            "statsforecast_cf",
            "pytorch_forecasting_tft",
        ]
    )
    planning_runtime_profile: str = "openai_responses_planning_research_v1"
    editing_runtime_profile: str = "openai_chat_edit_patch_v1"
    seed: int = 7
    intervention_t: int = 70
    n_units: int = 12
    n_periods: int = 120
    placebo_pre_rmspe_factor: float = 5.0
    min_pre_periods: int = 12
    max_time_placebos: int = 8
    deliverables: List[str] = field(
        default_factory=lambda: [
            "context_pack_json",
            "run_digest_json",
            "panel_report_markdown",
            "run_ledger_jsonl",
            "study_blueprint_json",
            "adapter_catalog_json",
            "runtime_profile_planning_json",
            "runtime_profile_editing_json",
        ]
    )
    constraints: List[str] = field(
        default_factory=lambda: [
            "prefer structured JSON over prose",
            "prefer minimal diffs and handles over full-file dumps",
            "do not inline large tables when a handle is available",
            "make outputs stable and reproducible",
            "separate retrieval turns from editing turns",
        ]
    )
    interaction_mode: str = "json_first"
    patch_policy: str = "minimal_diff"
    context_policy: str = "opaque_handles"
    tool_policy: str = "prefer_cli_then_python"
    orchestration_mode: str = "two_turn"
    planning_runtime: str = "tools_plus_structured_outputs"
    editing_runtime: str = "no_tools_predicted_output_when_available"
    token_budget: TokenBudget = field(default_factory=TokenBudget)

    def to_panel_experiment_spec(self) -> PanelExperimentSpec:
        return PanelExperimentSpec(
            dataset=self.dataset,
            model=self.model,
            seed=self.seed,
            intervention_t=self.intervention_t,
            n_units=self.n_units,
            n_periods=self.n_periods,
            placebo_pre_rmspe_factor=self.placebo_pre_rmspe_factor,
            min_pre_periods=self.min_pre_periods,
            max_time_placebos=self.max_time_placebos,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["token_budget"] = self.token_budget.to_dict()
        return payload

    def to_json(self, path: Union[str, Path], pretty: bool = True) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2 if pretty else None, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "AgentResearchTaskSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        budget = payload.get("token_budget", {}) or {}
        budget = {k: budget[k] for k in ["input_limit", "reserve_for_output", "reserve_for_instructions"] if k in budget}
        payload["token_budget"] = TokenBudget(**budget)
        return cls(**payload)

    @staticmethod
    def json_schema() -> Dict[str, Any]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "AgentResearchTaskSpec",
            "type": "object",
            "required": [
                "task_id",
                "objective",
                "task_family",
                "dataset",
                "model",
                "interaction_mode",
                "token_budget",
                "orchestration_mode",
                "planning_runtime",
                "editing_runtime",
                "planning_runtime_profile",
                "editing_runtime_profile",
            ],
            "properties": {
                "task_id": {"type": "string"},
                "objective": {"type": "string"},
                "task_family": {"type": "string", "enum": ["panel", "impact", "forecast_cf", "quasi_experiment"]},
                "research_track": {"type": "string"},
                "dataset": {"type": "string"},
                "dataset_suite": {"type": "array", "items": {"type": "string"}},
                "model": {"type": "string"},
                "candidate_adapters": {"type": "array", "items": {"type": "string"}},
                "planning_runtime_profile": {"type": "string"},
                "editing_runtime_profile": {"type": "string"},
                "seed": {"type": "integer"},
                "intervention_t": {"type": "integer"},
                "n_units": {"type": "integer"},
                "n_periods": {"type": "integer"},
                "placebo_pre_rmspe_factor": {"type": "number"},
                "min_pre_periods": {"type": "integer"},
                "max_time_placebos": {"type": "integer"},
                "deliverables": {"type": "array", "items": {"type": "string"}},
                "constraints": {"type": "array", "items": {"type": "string"}},
                "interaction_mode": {"type": "string", "enum": ["json_first", "mixed"]},
                "patch_policy": {"type": "string"},
                "context_policy": {"type": "string"},
                "tool_policy": {"type": "string"},
                "orchestration_mode": {"type": "string", "enum": ["single_turn", "two_turn", "multi_turn"]},
                "planning_runtime": {"type": "string"},
                "editing_runtime": {"type": "string"},
                "token_budget": {
                    "type": "object",
                    "required": ["input_limit", "reserve_for_output", "reserve_for_instructions"],
                    "properties": {
                        "input_limit": {"type": "integer"},
                        "reserve_for_output": {"type": "integer"},
                        "reserve_for_instructions": {"type": "integer"},
                    },
                },
            },
            "additionalProperties": False,
        }
