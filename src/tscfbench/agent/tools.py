from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from tscfbench.agent.artifacts import (
    list_artifacts,
    preview_tabular_artifact,
    read_text_artifact,
    search_text_artifact,
    summarize_manifest,
)
from tscfbench.agent.bundle import build_panel_agent_bundle
from tscfbench.agent.planner import build_context_plan
from tscfbench.agent.repo_map import build_repo_map, build_repo_map_text
from tscfbench.agent.runtime_profiles import export_runtime_profile, list_runtime_profiles, runtime_profile_catalog
from tscfbench.agent.specs import AgentResearchTaskSpec
from tscfbench.agent.templates import render_agents_md
from tscfbench.agent.tokens import TokenBudget
from tscfbench.datasets import list_dataset_cards
from tscfbench.canonical import (
    CanonicalBenchmarkSpec,
    list_canonical_studies,
    make_canonical_sweep_spec,
    render_canonical_markdown,
    run_canonical_benchmark,
)
from tscfbench.experiments import PanelExperimentSpec, materialize_panel_case, run_panel_experiment
from tscfbench.install_matrix import install_matrix_json, render_install_matrix_markdown
from tscfbench.product import (
    api_handbook,
    cli_guide,
    environment_profiles,
    package_overview,
    render_api_handbook_markdown,
    render_cli_guide_markdown,
    render_environment_profiles_markdown,
    render_package_overview_markdown,
    render_use_cases_markdown,
    use_case_catalog,
)
from tscfbench.guidebook import (
    benchmark_cards,
    recommend_start_path,
    render_benchmark_cards_markdown,
    render_start_here_markdown,
    render_workflow_recipes_markdown,
    workflow_recipes,
)
from tscfbench.narrative import (
    api_atlas,
    capability_map,
    package_story,
    render_api_atlas_markdown,
    render_capability_map_markdown,
    render_package_story_markdown,
    render_scenario_matrix_markdown,
    render_tutorial_index_markdown,
    scenario_matrix,
    tutorial_index,
    write_release_kit,
)
from tscfbench.showcases import (
    high_traffic_cases,
    public_data_sources,
    render_high_traffic_cases_markdown,
    render_public_data_sources_markdown,
)
from tscfbench.demo_cases import demo_catalog, render_demo_gallery_markdown, run_demo
from tscfbench.share_packages import make_share_package_for_demo
from tscfbench.onramp import doctor_report, render_doctor_markdown, run_quickstart
from tscfbench.positioning import (
    ecosystem_audit,
    feature_coverage_matrix,
    package_differentiators,
    render_agent_first_design_markdown,
    render_differentiators_markdown,
    render_docs_homepage_markdown,
    render_ecosystem_audit_markdown,
    render_feature_coverage_markdown,
    render_github_readme_markdown,
    write_positioning_assets,
)
from tscfbench.model_zoo import list_model_ids
from tscfbench.sweeps import SweepMatrixSpec, make_default_sweep_spec, render_sweep_markdown, run_sweep
from tscfbench.integrations.cards import adapter_catalog, recommend_adapter_stack
from tscfbench.report import render_panel_markdown
from tscfbench.study import build_research_study_blueprint


ToolHandler = Callable[[Dict[str, Any], Path], Dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    handler: ToolHandler
    output_schema: Optional[Dict[str, Any]] = None

    def to_openai_function(self, *, strict: bool = True, compact: bool = False) -> Dict[str, Any]:
        return {
            "type": "function",
            "name": self.name,
            "description": _compact_description(self.title if compact else self.description),
            "strict": bool(strict),
            "parameters": _compact_schema(self.input_schema) if compact else self.input_schema,
        }

    def to_mcp_tool(self) -> Dict[str, Any]:
        payload = {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
        if self.output_schema is not None:
            payload["outputSchema"] = self.output_schema
        return payload


def _compact_description(text: str) -> str:
    text = str(text or "").strip()
    if not text:
        return "Tool."
    if len(text) <= 72:
        return text
    first = text.split(".", 1)[0].strip()
    return first if first else text[:72].rstrip() + "…"


def _compact_schema(node: Any) -> Any:
    if isinstance(node, dict):
        out: Dict[str, Any] = {}
        for key, value in node.items():
            if key in {"$schema", "description", "title", "default"}:
                continue
            out[key] = _compact_schema(value)
        return out
    if isinstance(node, list):
        return [_compact_schema(v) for v in node]
    return node


def _schema_obj(properties: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": properties,
        "required": required or list(properties.keys()),
        "additionalProperties": False,
    }


def _s(description: str) -> Dict[str, Any]:
    return {"type": ["string", "null"], "description": description}


def _i(description: str) -> Dict[str, Any]:
    return {"type": ["integer", "null"], "description": description}


def _n(description: str) -> Dict[str, Any]:
    return {"type": ["number", "null"], "description": description}


def _b(description: str) -> Dict[str, Any]:
    return {"type": ["boolean", "null"], "description": description}


def _arr_str(description: str) -> Dict[str, Any]:
    return {"type": ["array", "null"], "items": {"type": "string"}, "description": description}


def _token_budget_from_args(args: Dict[str, Any]) -> TokenBudget:
    return TokenBudget(
        input_limit=int(args.get("input_limit") or 8000),
        reserve_for_output=int(args.get("reserve_for_output") or 2000),
        reserve_for_instructions=int(args.get("reserve_for_instructions") or 1000),
    )


def _agent_spec_from_args(args: Dict[str, Any]) -> AgentResearchTaskSpec:
    spec_path = args.get("spec_path")
    if spec_path:
        return AgentResearchTaskSpec.from_json(spec_path)
    return AgentResearchTaskSpec(
        task_id=str(args.get("task_id") or "panel_counterfactual_research"),
        objective=str(args.get("objective") or "Run a research-grade panel counterfactual benchmark and return concise, machine-readable artifacts."),
        task_family=str(args.get("task_family") or "panel"),
        dataset=str(args.get("dataset") or "synthetic_latent_factor"),
        model=str(args.get("model") or "simple_scm"),
        seed=int(args.get("seed") or 7),
        intervention_t=int(args.get("intervention_t") or 70),
        n_units=int(args.get("n_units") or 12),
        n_periods=int(args.get("n_periods") or 120),
        placebo_pre_rmspe_factor=float(args.get("placebo_pre_rmspe_factor") or 5.0),
        min_pre_periods=int(args.get("min_pre_periods") or 12),
        max_time_placebos=int(args.get("max_time_placebos") or 8),
        token_budget=_token_budget_from_args(args),
    )


def _panel_spec_from_args(args: Dict[str, Any]) -> PanelExperimentSpec:
    spec_path = args.get("spec_path")
    if spec_path:
        return PanelExperimentSpec.from_json(spec_path)
    return PanelExperimentSpec(
        dataset=str(args.get("dataset") or "synthetic_latent_factor"),
        model=str(args.get("model") or "simple_scm"),
        seed=int(args.get("seed") or 7),
        intervention_t=int(args.get("intervention_t") or 70),
        n_units=int(args.get("n_units") or 12),
        n_periods=int(args.get("n_periods") or 120),
        placebo_pre_rmspe_factor=float(args.get("placebo_pre_rmspe_factor") or 5.0),
        min_pre_periods=int(args.get("min_pre_periods") or 12),
        max_time_placebos=int(args.get("max_time_placebos") or 8),
    )


def _format_or_json_payload(*, format_: str, payload: Any, markdown: str, output_path: str | None = None) -> Dict[str, Any]:
    fmt = str(format_ or "json").lower()
    if fmt == "markdown":
        if output_path:
            Path(output_path).write_text(markdown, encoding="utf-8")
        return {"format": "markdown", "markdown": markdown, "output_path": output_path}
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return {"format": "json", "payload": payload, "output_path": output_path}


def _handle_package_overview(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=package_overview(),
        markdown=render_package_overview_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_api_handbook(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=api_handbook(),
        markdown=render_api_handbook_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_use_case_catalog(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=use_case_catalog(),
        markdown=render_use_cases_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_environment_profiles(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=environment_profiles(),
        markdown=render_environment_profiles_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_cli_guide(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=cli_guide(),
        markdown=render_cli_guide_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_package_story(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=package_story(),
        markdown=render_package_story_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_capability_map(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=capability_map(),
        markdown=render_capability_map_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_api_atlas(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=api_atlas(),
        markdown=render_api_atlas_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_scenario_matrix(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=scenario_matrix(),
        markdown=render_scenario_matrix_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_tutorial_index(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=tutorial_index(),
        markdown=render_tutorial_index_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_high_traffic_cases(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=high_traffic_cases(),
        markdown=render_high_traffic_cases_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_public_data_sources(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=public_data_sources(),
        markdown=render_public_data_sources_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_ecosystem_audit(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=ecosystem_audit(),
        markdown=render_ecosystem_audit_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_feature_coverage(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=feature_coverage_matrix(),
        markdown=render_feature_coverage_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_differentiators(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=package_differentiators(),
        markdown=render_differentiators_markdown(),
        output_path=args.get("output_path"),
    )



def _handle_github_readme(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    markdown = render_github_readme_markdown()
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(markdown, encoding="utf-8")
    return {"format": "markdown", "markdown": markdown, "output_path": output_path}



def _handle_website_home(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    markdown = render_docs_homepage_markdown()
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(markdown, encoding="utf-8")
    return {"format": "markdown", "markdown": markdown, "output_path": output_path}



def _handle_agent_first_design(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    markdown = render_agent_first_design_markdown()
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(markdown, encoding="utf-8")
    return {"format": "markdown", "markdown": markdown, "output_path": output_path}



def _handle_make_positioning_assets(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    output_dir = str(args.get("output_dir") or "positioning_assets")
    return write_positioning_assets(output_dir)



def _handle_make_release_kit(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    output_dir = str(args.get("output_dir") or "release_kit")
    return write_release_kit(output_dir)


def _handle_start_here(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    kwargs = {
        "persona": args.get("persona"),
        "task_family": args.get("task_family"),
        "environment": args.get("environment"),
        "goal": args.get("goal"),
        "need_agents": args.get("need_agents"),
    }
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=recommend_start_path(**kwargs),
        markdown=render_start_here_markdown(**kwargs),
        output_path=args.get("output_path"),
    )


def _handle_doctor(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=doctor_report(),
        markdown=render_doctor_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_run_quickstart(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    output_dir = str(args.get("output_dir") or "tscfbench_quickstart")
    payload = run_quickstart(
        output_dir,
        data_source=str(args.get("data_source") or "snapshot"),
        include_external=bool(args.get("include_external") if args.get("include_external") is not None else False),
        seed=int(args.get("seed") or 7),
        plot=bool(args.get("plot") if args.get("plot") is not None else True),
    )
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return payload


def _handle_list_demo_cases(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=demo_catalog(),
        markdown=render_demo_gallery_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_run_demo(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    demo_id = str(args.get("demo_id") or "city-traffic")
    output_dir = str(args.get("output_dir") or "tscfbench_demo")
    plot = bool(args.get("plot") if args.get("plot") is not None else True)
    payload = run_demo(demo_id, output_dir=output_dir, plot=plot)
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return payload


def _handle_make_share_package(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    demo_id = str(args.get("demo_id") or "repo-breakout")
    output_dir = str(args.get("output_dir") or "tscfbench_share_package")
    plot = bool(args.get("plot") if args.get("plot") is not None else True)
    payload = make_share_package_for_demo(demo_id, output_dir=output_dir, plot=plot)
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return payload


def _handle_workflow_recipes(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=workflow_recipes(),
        markdown=render_workflow_recipes_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_benchmark_cards(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=benchmark_cards(),
        markdown=render_benchmark_cards_markdown(),
        output_path=args.get("output_path"),
    )


def _handle_recommend_path(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    kwargs = {
        "persona": args.get("persona"),
        "task_family": args.get("task_family"),
        "environment": args.get("environment"),
        "goal": args.get("goal"),
        "need_agents": args.get("need_agents"),
        "top_k": int(args.get("top_k") or 3),
    }
    return _format_or_json_payload(
        format_=str(args.get("format") or "json"),
        payload=recommend_start_path(**kwargs),
        markdown=render_start_here_markdown(
            persona=kwargs["persona"],
            task_family=kwargs["task_family"],
            environment=kwargs["environment"],
            goal=kwargs["goal"],
            need_agents=kwargs["need_agents"],
        ),
        output_path=args.get("output_path"),
    )


def _handle_list_datasets(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return {
        "datasets": [
            {
                "id": c.id,
                "task_type": c.task_type,
                "title": c.title,
                "treated_unit": c.treated_unit,
                "intervention_t": c.intervention_t,
                "outcome": c.outcome,
                "summary": c.summary,
                "source": c.source,
            }
            for c in list_dataset_cards()
        ]
    }


def _handle_install_matrix(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    format_ = str(args.get("format") or "json").lower()
    if format_ == "markdown":
        text = render_install_matrix_markdown()
        output_path = args.get("output_path")
        if output_path:
            Path(output_path).write_text(text, encoding="utf-8")
        return {"format": "markdown", "markdown": text}
    rows = install_matrix_json()
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"format": "json", "rows": rows}


def _handle_list_canonical_studies(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return {"studies": [s.to_dict() for s in list_canonical_studies()]}


def _handle_make_canonical_spec(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    study_ids = args.get("study_ids") or None
    models = args.get("models") or None
    spec = CanonicalBenchmarkSpec(
        name=str(args.get("name") or "canonical_panel_benchmark"),
        study_ids=list(study_ids) if study_ids is not None else [s.id for s in list_canonical_studies()],
        models=list(models) if models is not None else None,
        include_external=bool(args.get("include_external") if args.get("include_external") is not None else True),
        data_source=str(args.get("data_source") or "auto"),
        seed=int(args.get("seed") or 7),
        stop_on_error=bool(args.get("stop_on_error") if args.get("stop_on_error") is not None else False),
    )
    payload = spec.to_dict()
    output_path = args.get("output_path")
    if output_path:
        spec.to_json(output_path)
    return payload


def _handle_run_canonical(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec_path = args.get("spec_path")
    if spec_path:
        spec = CanonicalBenchmarkSpec.from_json(spec_path)
    else:
        spec = CanonicalBenchmarkSpec(
            name=str(args.get("name") or "canonical_panel_benchmark"),
            study_ids=list(args.get("study_ids") or [s.id for s in list_canonical_studies()]),
            models=list(args.get("models") or [] ) or None,
            include_external=bool(args.get("include_external") if args.get("include_external") is not None else False),
            data_source=str(args.get("data_source") or "snapshot"),
            seed=int(args.get("seed") or 7),
            stop_on_error=bool(args.get("stop_on_error") if args.get("stop_on_error") is not None else False),
        )
    run = run_canonical_benchmark(spec)
    payload = {"summary": run.summary(), "results": run.to_frame().to_dict(orient="records")}
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    report_path = args.get("report_path")
    if report_path:
        Path(report_path).write_text(render_canonical_markdown(run), encoding="utf-8")
    return payload


def _handle_list_adapters(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    task_family = args.get("task_family")
    rows = adapter_catalog(include_availability=True)
    if task_family:
        rows = [row for row in rows if row.get("task_family") == task_family or (task_family == "panel" and row.get("task_family") == "quasi_experiment")]
    return {"adapters": rows}


def _handle_recommend_stack(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return {
        "recommendations": recommend_adapter_stack(
            task_family=str(args.get("task_family") or "panel"),
            goal=str(args.get("goal") or "research"),
            token_aware=bool(args.get("token_aware") if args.get("token_aware") is not None else True),
            max_adapters=int(args.get("max_adapters") or 6),
        )
    }


def _handle_list_model_ids(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return {"model_ids": list_model_ids(task_family=args.get("task_family"))}


def _handle_make_sweep_spec(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec = make_default_sweep_spec(
        task_family=str(args.get("task_family") or "panel"),
        include_external=bool(args.get("include_external") if args.get("include_external") is not None else True),
        seed=int(args.get("seed") or 7),
    )
    payload = spec.to_dict()
    output_path = args.get("output_path")
    if output_path:
        spec.to_json(output_path)
    return payload


def _handle_run_sweep(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec_path = args.get("spec_path")
    if spec_path:
        spec = SweepMatrixSpec.from_json(spec_path)
    else:
        spec = make_default_sweep_spec(
            task_family=str(args.get("task_family") or "panel"),
            include_external=bool(args.get("include_external") if args.get("include_external") is not None else True),
            seed=int(args.get("seed") or 7),
        )
    run = run_sweep(spec)
    payload = {"summary": run.summary(), "results": run.to_frame().to_dict(orient="records")}
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    report_path = args.get("report_path")
    if report_path:
        Path(report_path).write_text(render_sweep_markdown(run), encoding="utf-8")
    return payload


def _handle_list_runtime_profiles(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    return {"profiles": runtime_profile_catalog()}


def _handle_export_runtime_profile(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    profile_id = args.get("profile_id") or "openai_responses_planning_research_v1"
    payload = export_runtime_profile(str(profile_id))
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return payload


def _handle_make_agent_spec(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec = _agent_spec_from_args(args)
    payload = spec.to_dict()
    output_path = args.get("output_path")
    if output_path:
        spec.to_json(output_path, pretty=True)
    return payload


def _handle_make_study_blueprint(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec = _agent_spec_from_args(args)
    blueprint = build_research_study_blueprint(spec, max_adapters=int(args.get("max_adapters") or 8))
    payload = blueprint.to_dict()
    output_path = args.get("output_path")
    if output_path:
        blueprint.to_json(output_path, pretty=True)
    return payload


def _handle_build_agent_bundle(args: Dict[str, Any], repo_root: Path) -> Dict[str, Any]:
    spec = _agent_spec_from_args(args)
    bundle = build_panel_agent_bundle(
        spec,
        output_dir=args.get("output_dir") or "bundle_dir",
        include_repo_map=bool(args.get("include_repo_map") if args.get("include_repo_map") is not None else True),
        repo_root=args.get("repo_root") or repo_root,
    )
    return bundle.to_dict()


def _handle_run_panel_experiment(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    spec = _panel_spec_from_args(args)
    report = run_panel_experiment(spec)
    report_path = args.get("report_path")
    if report_path:
        case = materialize_panel_case(spec)
        Path(report_path).write_text(render_panel_markdown(case, report), encoding="utf-8")
    return {
        "metrics": report.metrics,
        "space_placebos_head": report.space_placebos.head(8).to_dict(orient="records"),
        "time_placebos_head": report.time_placebos.head(8).to_dict(orient="records"),
    }


def _handle_repo_map(args: Dict[str, Any], repo_root: Path) -> Dict[str, Any]:
    root = Path(args.get("root") or repo_root).resolve()
    if bool(args.get("as_text")):
        return {"repo_map_text": build_repo_map_text(root, query=args.get("query"), max_files=int(args.get("max_files") or 12), include_tests=bool(args.get("include_tests") if args.get("include_tests") is not None else True))}
    return {"repo_map": [e.to_dict() for e in build_repo_map(root, query=args.get("query"), max_files=int(args.get("max_files") or 12), include_tests=bool(args.get("include_tests") if args.get("include_tests") is not None else True))]}


def _handle_list_artifacts(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    manifest_path = args.get("manifest_path")
    if not manifest_path:
        raise ValueError("manifest_path is required")
    return {"manifest_summary": summarize_manifest(manifest_path), "artifacts": list_artifacts(manifest_path)}


def _handle_read_artifact(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    manifest_path = args.get("manifest_path")
    if not manifest_path:
        raise ValueError("manifest_path is required")
    return read_text_artifact(
        manifest_path,
        artifact_id=args.get("artifact_id"),
        kind=args.get("kind"),
        path=args.get("path"),
        offset_chars=int(args.get("offset_chars") or 0),
        max_chars=int(args.get("max_chars") or 1200),
    )


def _handle_search_artifact(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    manifest_path = args.get("manifest_path")
    query = args.get("query")
    if not manifest_path or not query:
        raise ValueError("manifest_path and query are required")
    return search_text_artifact(
        manifest_path,
        artifact_id=args.get("artifact_id"),
        kind=args.get("kind"),
        path=args.get("path"),
        query=str(query),
        max_hits=int(args.get("max_hits") or 8),
    )


def _handle_preview_artifact_table(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    manifest_path = args.get("manifest_path")
    if not manifest_path:
        raise ValueError("manifest_path is required")
    return preview_tabular_artifact(
        manifest_path,
        artifact_id=args.get("artifact_id"),
        kind=args.get("kind"),
        path=args.get("path"),
        rows=int(args.get("rows") or 8),
        columns=args.get("columns") or None,
    )


def _handle_plan_context(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    manifest_path = args.get("manifest_path")
    if not manifest_path:
        raise ValueError("manifest_path is required")
    return build_context_plan(
        manifest_path,
        phase=str(args.get("phase") or "triage"),
        max_tokens=int(args.get("max_tokens") or 2800),
        query=args.get("query"),
        include_repo_map=bool(args.get("include_repo_map") if args.get("include_repo_map") is not None else True),
    )


def _handle_write_agents_md(args: Dict[str, Any], _: Path) -> Dict[str, Any]:
    text = render_agents_md(project_name=str(args.get("project_name") or "tscfbench"))
    output_path = args.get("output_path")
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return {"text": text, "output_path": output_path}


_TOOLS: List[ToolSpec] = [
    ToolSpec("tscf_package_overview", "Package overview", "Explain what tscfbench is, why it exists, who it is for, and what outputs it produces.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_package_overview),
    ToolSpec("tscf_api_handbook", "API handbook", "Describe the major API layers of tscfbench, why each layer exists, when to use it, and what it returns.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_api_handbook),
    ToolSpec("tscf_use_case_catalog", "Use-case catalog", "List practical research, teaching, CI, and agent-workflow scenarios that tscfbench is designed to support.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_use_case_catalog),
    ToolSpec("tscf_environment_profiles", "Environment profiles", "Explain which parts of tscfbench work best in notebooks, CLI workflows, CI, agent environments, and shared compute.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_environment_profiles),
    ToolSpec("tscf_cli_guide", "CLI guide", "Describe the major CLI command groups and what type of user each group is for.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_cli_guide),
    ToolSpec("tscf_package_story", "Package story", "Give the product-level explanation of what tscfbench is, what it is not, and why researchers adopt it.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_package_story),
    ToolSpec("tscf_capability_map", "Capability map", "Explain which capability layer exists for which job, why it exists, and what it outputs.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_capability_map),
    ToolSpec("tscf_api_atlas", "API atlas", "Combine the package story, capability map, and API handbook into one guided surface for choosing the right API layer.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_api_atlas),
    ToolSpec("tscf_scenario_matrix", "Scenario matrix", "Map real research situations to the APIs, environments, and outputs that fit them best.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_scenario_matrix),
    ToolSpec("tscf_tutorial_index", "Tutorial index", "List tutorials by audience, environment, and time-to-first-result so new users can choose a path quickly.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_tutorial_index),
    ToolSpec("tscf_start_here", "Start here", "Give a plain-language package introduction plus a recommended first path based on persona, task family, environment, and goal.", _schema_obj({"persona": _s("Persona hint such as new researcher or applied researcher."), "task_family": _s("Task family such as overview, panel, impact, or research_ops."), "environment": _s("Environment such as notebook, cli, ci, or agent."), "goal": _s("Goal such as understand, benchmark, own data, or compare."), "need_agents": _b("Whether the workflow explicitly involves coding agents."), "format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_start_here),
    ToolSpec("tscf_workflow_recipes", "Workflow recipes", "List scenario-first recipes that explain which API, docs, notebooks, and outputs fit each type of user workflow.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_workflow_recipes),
    ToolSpec("tscf_benchmark_cards", "Benchmark cards", "List benchmark and study cards that explain what each canonical or synthetic benchmark is for and where it is most useful.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_benchmark_cards),
    ToolSpec("tscf_high_traffic_cases", "High-traffic cases", "List public-facing, high-attention case ideas such as GitHub-star surges, crypto event studies, and commodity shock cases.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_high_traffic_cases),
    ToolSpec("tscf_public_data_sources", "Public data sources", "Describe public data sources and loader patterns for GitHub-star, crypto, and commodity event studies.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_public_data_sources),
    ToolSpec("tscf_ecosystem_audit", "Ecosystem audit", "Compare tscfbench with adjacent packages and explain where it fits in the ecosystem.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_ecosystem_audit),
    ToolSpec("tscf_feature_coverage", "Feature coverage", "Render a package coverage matrix showing the primary documented focus of tscfbench and adjacent packages.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_feature_coverage),
    ToolSpec("tscf_differentiators", "Differentiators", "Summarize the main reasons tscfbench is different from specialist estimator packages.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_differentiators),
    ToolSpec("tscf_github_readme", "GitHub README", "Generate a GitHub-ready README that explains what tscfbench is, how it differs, and how to start.", _schema_obj({"output_path": _s("Optional output path.")}), _handle_github_readme),
    ToolSpec("tscf_website_home", "Website home", "Generate a docs-site landing page for tscfbench.", _schema_obj({"output_path": _s("Optional output path.")}), _handle_website_home),
    ToolSpec("tscf_agent_first_design", "Agent-first design", "Explain the token-aware, agent-friendly design principles behind the package.", _schema_obj({"output_path": _s("Optional output path.")}), _handle_agent_first_design),
    ToolSpec("tscf_recommend_path", "Recommend path", "Recommend a first workflow path and next artifacts based on persona, task family, environment, goal, and agent needs.", _schema_obj({"persona": _s("Persona hint such as applied researcher or research engineer."), "task_family": _s("Task family such as panel, impact, or research_ops."), "environment": _s("Environment such as notebook, cli, ci, or agent."), "goal": _s("Goal such as benchmark, own data, understand, compare, or automation."), "need_agents": _b("Whether coding agents are part of the workflow."), "top_k": _i("Maximum number of recommended recipes."), "format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_recommend_path),
    ToolSpec("tscf_list_datasets", "List datasets", "List built-in benchmark dataset cards for time-series counterfactual research.", _schema_obj({}, required=[]), _handle_list_datasets),
    ToolSpec("tscf_install_matrix", "Installation matrix", "Return the structured installation matrix for optional third-party counterfactual libraries.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_install_matrix),
    ToolSpec("tscf_list_canonical_studies", "List canonical studies", "List canonical benchmark studies such as German reunification, Prop99, and Basque Country.", _schema_obj({}, required=[]), _handle_list_canonical_studies),
    ToolSpec("tscf_make_canonical_spec", "Make canonical benchmark spec", "Create a canonical benchmark spec spanning Germany, Prop99, Basque, or a selected subset.", _schema_obj({"name": _s("Benchmark name."), "study_ids": _arr_str("Optional study ids."), "models": _arr_str("Optional explicit model ids."), "include_external": _b("Whether to include external adapters."), "data_source": _s("auto, remote, or snapshot."), "seed": _i("Random seed."), "stop_on_error": _b("Whether to stop on the first error."), "output_path": _s("Optional JSON output path.")}), _handle_make_canonical_spec),
    ToolSpec("tscf_run_canonical", "Run canonical benchmark", "Run the canonical benchmark spec and optionally write JSON and Markdown outputs.", _schema_obj({"spec_path": _s("Optional CanonicalBenchmarkSpec path."), "name": _s("Benchmark name when spec_path is not supplied."), "study_ids": _arr_str("Optional study ids."), "models": _arr_str("Optional model ids."), "include_external": _b("Whether to include external adapters."), "data_source": _s("auto, remote, or snapshot."), "seed": _i("Random seed."), "stop_on_error": _b("Whether to stop on first error."), "output_path": _s("Optional JSON output path."), "report_path": _s("Optional Markdown report output path.")}), _handle_run_canonical),
    ToolSpec("tscf_list_adapters", "List adapters", "List built-in and optional adapter cards, including availability and install hints.", _schema_obj({"task_family": _s("Optional task family filter such as panel or impact.")}), _handle_list_adapters),
    ToolSpec("tscf_recommend_stack", "Recommend adapter stack", "Recommend a research-oriented or token-aware adapter stack for a task family.", _schema_obj({"task_family": _s("Task family such as panel, impact, or forecast_cf."), "goal": _s("Goal such as research or engineering."), "token_aware": _b("Whether to prefer agent-friendly / lower-token adapters."), "max_adapters": _i("Maximum adapters to return.")}), _handle_recommend_stack),
    ToolSpec("tscf_list_model_ids", "List model ids", "List runnable model ids exposed by the model zoo for a task family.", _schema_obj({"task_family": _s("Optional task family filter such as panel, impact, or forecast_cf.")}), _handle_list_model_ids),
    ToolSpec("tscf_make_sweep_spec", "Make sweep spec", "Create a default sweep matrix spec for panel or impact experiments.", _schema_obj({"task_family": _s("Task family such as panel or impact."), "include_external": _b("Whether to include external adapters."), "seed": _i("Random seed."), "output_path": _s("Optional output path for the sweep spec JSON.")}), _handle_make_sweep_spec),
    ToolSpec("tscf_run_sweep", "Run sweep", "Run a sweep matrix and return compact per-cell results while recording adapter errors instead of crashing.", _schema_obj({"spec_path": _s("Optional existing SweepMatrixSpec JSON path."), "task_family": _s("Task family used when spec_path is not provided."), "include_external": _b("Whether to include external adapters when spec_path is not provided."), "seed": _i("Random seed when spec_path is not provided."), "output_path": _s("Optional JSON output path."), "report_path": _s("Optional markdown report output path.")}), _handle_run_sweep),
    ToolSpec("tscf_list_runtime_profiles", "List runtime profiles", "List runtime profiles for planning, analysis, and editing turns.", _schema_obj({}, required=[]), _handle_list_runtime_profiles),
    ToolSpec("tscf_export_runtime_profile", "Export runtime profile", "Export a ready-to-use runtime profile and request template for OpenAI API calls.", _schema_obj({"profile_id": _s("Runtime profile id."), "output_path": _s("Optional JSON output path.")}), _handle_export_runtime_profile),
    ToolSpec("tscf_make_agent_spec", "Make agent spec", "Create a compact JSON-first research task spec for token-efficient benchmark work.", _schema_obj({"spec_path": _s("Optional existing AgentResearchTaskSpec JSON path to load instead of building fields."), "task_id": _s("Task identifier."), "objective": _s("Research objective."), "task_family": _s("Task family such as panel or impact."), "dataset": _s("Dataset id."), "model": _s("Model id such as simple_scm or did."), "seed": _i("Random seed."), "intervention_t": _i("Intervention time index or year."), "n_units": _i("Synthetic dataset unit count when applicable."), "n_periods": _i("Synthetic dataset period count when applicable."), "placebo_pre_rmspe_factor": _n("Eligibility factor for placebo screening."), "min_pre_periods": _i("Minimum pre-periods for time placebos."), "max_time_placebos": _i("Maximum time placebos."), "input_limit": _i("Input token limit for the target runtime."), "reserve_for_output": _i("Reserved output tokens."), "reserve_for_instructions": _i("Reserved instruction tokens."), "output_path": _s("Optional output path for writing the JSON file.")}), _handle_make_agent_spec),
    ToolSpec("tscf_make_study_blueprint", "Make study blueprint", "Create a research study blueprint linking datasets, adapters, protocol, and runtime profiles.", _schema_obj({"spec_path": _s("Optional AgentResearchTaskSpec JSON path."), "task_id": _s("Task identifier."), "objective": _s("Research objective."), "task_family": _s("Task family such as panel."), "dataset": _s("Primary dataset id."), "model": _s("Primary model id."), "max_adapters": _i("Maximum adapters in the recommendation set."), "output_path": _s("Optional output path for the blueprint JSON.")}), _handle_make_study_blueprint),
    ToolSpec("tscf_build_agent_bundle", "Build agent bundle", "Run a panel benchmark and materialize an agent-native artifact bundle with study blueprints, adapter catalog, runtime profiles, context packs, digests, context plans, and manifests.", _schema_obj({"spec_path": _s("Optional existing AgentResearchTaskSpec JSON path to load."), "task_id": _s("Task identifier."), "objective": _s("Research objective."), "dataset": _s("Dataset id."), "model": _s("Model id such as simple_scm or did."), "seed": _i("Random seed."), "intervention_t": _i("Intervention time index or year."), "n_units": _i("Synthetic dataset unit count when applicable."), "n_periods": _i("Synthetic dataset period count when applicable."), "placebo_pre_rmspe_factor": _n("Eligibility factor for placebo screening."), "min_pre_periods": _i("Minimum pre-periods for time placebos."), "max_time_placebos": _i("Maximum time placebos."), "input_limit": _i("Input token limit for the target runtime."), "reserve_for_output": _i("Reserved output tokens."), "reserve_for_instructions": _i("Reserved instruction tokens."), "output_dir": _s("Directory to write the bundle into."), "include_repo_map": _b("Whether to include a repo map in the bundle."), "repo_root": _s("Optional repository root override for repo map generation.")}), _handle_build_agent_bundle),
    ToolSpec("tscf_run_panel_experiment", "Run panel experiment", "Run a panel counterfactual experiment and return compact metrics plus placebo previews.", _schema_obj({"spec_path": _s("Optional existing PanelExperimentSpec JSON path to load."), "dataset": _s("Dataset id."), "model": _s("Model id such as simple_scm or did."), "seed": _i("Random seed."), "intervention_t": _i("Intervention time index or year."), "n_units": _i("Synthetic dataset unit count when applicable."), "n_periods": _i("Synthetic dataset period count when applicable."), "placebo_pre_rmspe_factor": _n("Eligibility factor for placebo screening."), "min_pre_periods": _i("Minimum pre-periods for time placebos."), "max_time_placebos": _i("Maximum time placebos."), "report_path": _s("Optional markdown report output path.")}), _handle_run_panel_experiment),
    ToolSpec("tscf_repo_map", "Build repo map", "Generate a compact repository map so coding agents can navigate the codebase with fewer tokens.", _schema_obj({"root": _s("Repository root path. Null means server root."), "query": _s("Optional query string to rank files."), "max_files": _i("Maximum files to include."), "include_tests": _b("Whether to include tests."), "as_text": _b("Return a text repo map instead of structured JSON.")}), _handle_repo_map),
    ToolSpec("tscf_list_artifacts", "List artifacts", "List artifact handles from a bundle manifest and summarize token footprint.", _schema_obj({"manifest_path": _s("Path to manifest.json.")}), _handle_list_artifacts),
    ToolSpec("tscf_read_artifact", "Read artifact slice", "Read a bounded text slice from an artifact handle to avoid loading the full file into context.", _schema_obj({"manifest_path": _s("Path to manifest.json."), "artifact_id": _s("Artifact id."), "kind": _s("Artifact kind, such as dataset_long or prediction_frame."), "path": _s("Artifact file name or path."), "offset_chars": _i("Starting character offset."), "max_chars": _i("Maximum characters to return.")}), _handle_read_artifact),
    ToolSpec("tscf_search_artifact", "Search artifact", "Search a text artifact for specific terms and return matched lines only.", _schema_obj({"manifest_path": _s("Path to manifest.json."), "artifact_id": _s("Artifact id."), "kind": _s("Artifact kind."), "path": _s("Artifact file name or path."), "query": _s("Case-insensitive query string."), "max_hits": _i("Maximum number of hits to return.")}), _handle_search_artifact),
    ToolSpec("tscf_preview_artifact_table", "Preview artifact table", "Preview the first few rows of a CSV or JSON artifact without loading the whole table.", _schema_obj({"manifest_path": _s("Path to manifest.json."), "artifact_id": _s("Artifact id."), "kind": _s("Artifact kind."), "path": _s("Artifact file name or path."), "rows": _i("Number of rows to return."), "columns": _arr_str("Optional subset of columns.")}), _handle_preview_artifact_table),
    ToolSpec("tscf_plan_context", "Plan context window", "Assemble a token-bounded context plan for triage, analysis, editing, or report-writing phases.", _schema_obj({"manifest_path": _s("Path to manifest.json."), "phase": _s("One of triage, analysis, editing, or report."), "max_tokens": _i("Maximum tokens for the assembled context."), "query": _s("Optional focus query for repo-map selection."), "include_repo_map": _b("Whether to include a repo map snippet when available.")}), _handle_plan_context),
    ToolSpec("tscf_write_agents_md", "Write AGENTS.md", "Generate an AGENTS.md template tuned for token-efficient research and coding workflows.", _schema_obj({"project_name": _s("Project name for the template."), "output_path": _s("Optional output path for AGENTS.md.")}), _handle_write_agents_md),
    ToolSpec("tscf_make_release_kit", "Make release kit", "Generate a directory of release-facing markdown assets such as a package story, API atlas, scenario matrix, and tutorial index.", _schema_obj({"output_dir": _s("Directory to write the release kit into.")}), _handle_make_release_kit),
    ToolSpec("tscf_make_positioning_assets", "Make positioning assets", "Generate GitHub- and website-facing positioning assets such as ecosystem audit, feature coverage, and README copy.", _schema_obj({"output_dir": _s("Directory to write the positioning assets into.")}), _handle_make_positioning_assets),
    ToolSpec("tscf_doctor", "Environment doctor", "Report whether the built-in path is ready, which optional backends are missing, and what the safest next command is.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_doctor),
    ToolSpec("tscf_run_quickstart", "Run quickstart", "Run the narrow quickstart path and return summary, generated files, and the next recommended command.", _schema_obj({"output_dir": _s("Directory to write quickstart outputs into."), "data_source": _s("snapshot, auto, or remote."), "include_external": _b("Whether to include optional external backends."), "seed": _i("Random seed."), "plot": _b("Whether to emit shareable chart assets when plotting support is available."), "output_path": _s("Optional JSON output path.")}), _handle_run_quickstart),
    ToolSpec("tscf_list_demo_cases", "List demo cases", "List chart-first demo cases such as city traffic, product launch, heatwave health, GitHub stars, and crypto events.", _schema_obj({"format": _s("json or markdown."), "output_path": _s("Optional output path.")}), _handle_list_demo_cases),
    ToolSpec("tscf_run_demo", "Run demo", "Run one demo case and return summary plus generated chart/report assets.", _schema_obj({"demo_id": _s("Demo id such as city-traffic, product-launch, heatwave-health, github-stars, or crypto-event."), "output_dir": _s("Directory to write demo outputs into."), "plot": _b("Whether to emit shareable chart assets when plotting support is available."), "output_path": _s("Optional JSON output path.")}), _handle_run_demo),
    ToolSpec("tscf_make_share_package", "Make share package", "Run one named demo and write a share-ready package containing a chart, share card, short summary, citation block, and manifest.", _schema_obj({"demo_id": _s("Demo id such as city-traffic, climate-grid, hospital-surge, or repo-breakout."), "output_dir": _s("Directory to write the share package into."), "plot": _b("Whether to emit shareable chart assets when plotting support is available."), "output_path": _s("Optional JSON output path.")}), _handle_make_share_package),

]

_TOOL_PROFILE_ROWS: Dict[str, Dict[str, Any]] = {
    "starter": {
        "summary": "Narrowest possible onboarding surface for quickstart, one named demo, and one share package.",
        "recommended_for": "first run, broad users, very tight token budgets",
        "aliases": ["default", "onboarding", "beginner"],
        "tool_names": [
            "tscf_start_here",
            "tscf_doctor",
            "tscf_run_quickstart",
            "tscf_list_demo_cases",
            "tscf_run_demo",
            "tscf_make_share_package",
        ],
    },
    "minimal": {
        "summary": "Starter-plus surface for quickstart, one named demo, a share package, and a compact agent handoff.",
        "recommended_for": "first successful run plus a bounded handoff to agents",
        "aliases": ["compact", "narrow"],
        "tool_names": [
            "tscf_start_here",
            "tscf_doctor",
            "tscf_run_quickstart",
            "tscf_make_canonical_spec",
            "tscf_list_demo_cases",
            "tscf_run_demo",
            "tscf_make_share_package",
            "tscf_make_agent_spec",
            "tscf_build_agent_bundle",
        ],
    },
    "research": {
        "summary": "Balanced research surface for canonical studies, sweeps, adapters, demos, and bounded artifact reads.",
        "recommended_for": "research engineers and methods users after the first successful run",
        "aliases": ["agent", "balanced"],
        "tool_names": [
            "tscf_start_here",
            "tscf_doctor",
            "tscf_list_canonical_studies",
            "tscf_make_canonical_spec",
            "tscf_run_canonical",
            "tscf_list_adapters",
            "tscf_recommend_stack",
            "tscf_list_model_ids",
            "tscf_make_sweep_spec",
            "tscf_run_sweep",
            "tscf_list_demo_cases",
            "tscf_run_demo",
            "tscf_make_share_package",
            "tscf_export_runtime_profile",
            "tscf_make_agent_spec",
            "tscf_build_agent_bundle",
            "tscf_list_artifacts",
            "tscf_read_artifact",
            "tscf_plan_context",
        ],
    },
    "full": {
        "summary": "Complete tool surface for full package introspection, docs generation, release assets, and deep automation.",
        "recommended_for": "full MCP servers and deep integrations",
        "aliases": ["all", "complete"],
        "tool_names": [tool.name for tool in _TOOLS],
    },
}


def _resolve_tool_profile(profile: str | None) -> str:
    key = str(profile or "minimal").strip().lower()
    if key in _TOOL_PROFILE_ROWS:
        return key
    for profile_id, row in _TOOL_PROFILE_ROWS.items():
        if key in {alias.lower() for alias in row.get("aliases", [])}:
            return profile_id
    raise KeyError(f"Unknown tool profile: {profile}")


def tool_profile_catalog() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for profile_id, row in _TOOL_PROFILE_ROWS.items():
        rows.append(
            {
                "id": profile_id,
                "summary": row["summary"],
                "recommended_for": row["recommended_for"],
                "aliases": list(row.get("aliases", [])),
                "tool_names": list(row["tool_names"]),
                "tool_count": len(row["tool_names"]),
            }
        )
    return rows


def list_tool_profiles() -> List[Dict[str, Any]]:
    return tool_profile_catalog()


def _tool_specs_for_profile(profile: str | None) -> List[ToolSpec]:
    profile_id = _resolve_tool_profile(profile)
    names = set(_TOOL_PROFILE_ROWS[profile_id]["tool_names"])
    return [tool for tool in _TOOLS if tool.name in names]



def get_tool_registry() -> Dict[str, ToolSpec]:
    return {tool.name: tool for tool in _TOOLS}



def list_tool_specs(profile: str | None = None) -> List[ToolSpec]:
    if profile is None:
        return list(_TOOLS)
    return _tool_specs_for_profile(profile)



def export_openai_function_tools(*, strict: bool = True, profile: str = "full", compact: bool | None = None) -> List[Dict[str, Any]]:
    compact_mode = (profile in {"starter", "minimal", "research"}) if compact is None else bool(compact)
    return [tool.to_openai_function(strict=strict, compact=compact_mode) for tool in _tool_specs_for_profile(profile)]



def invoke_tool(name: str, args: Optional[Dict[str, Any]] = None, *, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    registry = get_tool_registry()
    if name not in registry:
        raise KeyError(f"Unknown tool: {name}")
    safe_args = args or {}
    root = Path(repo_root or ".").resolve()
    return registry[name].handler(safe_args, root)



def export_tool_catalog_json(pretty: bool = True, profile: str | None = None) -> str:
    payload = [
        {
            "name": tool.name,
            "title": tool.title,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema,
        }
        for tool in list_tool_specs(profile)
    ]
    return json.dumps(payload, indent=2 if pretty else None, ensure_ascii=False, sort_keys=True)
