from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from tscfbench.agent.artifacts import iter_artifact_refs, summarize_manifest
from tscfbench.agent.context import pack_panel_case, pack_panel_run
from tscfbench.agent.ledger import RunLedger
from tscfbench.agent.planner import build_context_plan
from tscfbench.agent.repo_map import build_repo_map_text
from tscfbench.agent.runtime_profiles import export_runtime_profile
from tscfbench.agent.specs import AgentResearchTaskSpec
from tscfbench.experiments import PanelExperimentSpec, materialize_panel_case, materialize_panel_model
from tscfbench.integrations.cards import adapter_catalog
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel
from tscfbench.report import render_panel_markdown
from tscfbench.study import build_research_study_blueprint


@dataclass(frozen=True)
class PanelAgentBundle:
    run_id: str
    root_dir: str
    manifest_path: str
    context_pack_path: str
    run_digest_path: str
    report_path: str
    ledger_path: str
    triage_plan_path: Optional[str] = None
    analysis_plan_path: Optional[str] = None
    editing_plan_path: Optional[str] = None
    stats_path: Optional[str] = None
    study_blueprint_path: Optional[str] = None
    adapter_catalog_path: Optional[str] = None
    runtime_planning_path: Optional[str] = None
    runtime_editing_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "root_dir": self.root_dir,
            "manifest_path": self.manifest_path,
            "context_pack_path": self.context_pack_path,
            "run_digest_path": self.run_digest_path,
            "report_path": self.report_path,
            "ledger_path": self.ledger_path,
            "triage_plan_path": self.triage_plan_path,
            "analysis_plan_path": self.analysis_plan_path,
            "editing_plan_path": self.editing_plan_path,
            "stats_path": self.stats_path,
            "study_blueprint_path": self.study_blueprint_path,
            "adapter_catalog_path": self.adapter_catalog_path,
            "runtime_planning_path": self.runtime_planning_path,
            "runtime_editing_path": self.runtime_editing_path,
        }


def _to_panel_spec(spec: Union[AgentResearchTaskSpec, PanelExperimentSpec]) -> PanelExperimentSpec:
    if isinstance(spec, AgentResearchTaskSpec):
        return spec.to_panel_experiment_spec()
    return spec


def build_panel_agent_bundle(
    spec: Union[AgentResearchTaskSpec, PanelExperimentSpec],
    output_dir: Union[str, Path],
    include_repo_map: bool = True,
    repo_root: Optional[Union[str, Path]] = None,
) -> PanelAgentBundle:
    panel_spec = _to_panel_spec(spec)
    if isinstance(spec, AgentResearchTaskSpec):
        budget = spec.token_budget
        agent_spec_payload = spec.to_dict()
        agent_spec = spec
    else:
        from tscfbench.agent.tokens import TokenBudget

        budget = TokenBudget()
        agent_spec_payload = panel_spec.__dict__.copy()
        agent_spec = AgentResearchTaskSpec(dataset=panel_spec.dataset, model=panel_spec.model)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"panel-{uuid.uuid4().hex[:12]}"
    ledger = RunLedger(output_dir / "run_ledger.jsonl", run_id=run_id)
    ledger.append("bundle_started", {"dataset": panel_spec.dataset, "model": panel_spec.model})

    agent_spec_path = output_dir / "agent_spec.json"
    agent_spec_path.write_text(json.dumps(agent_spec_payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("agent_spec_written", {"path": str(agent_spec_path)})

    study_blueprint = build_research_study_blueprint(agent_spec)
    study_blueprint_path = output_dir / "study_blueprint.json"
    study_blueprint.to_json(study_blueprint_path, pretty=True)
    ledger.append("study_blueprint_written", {"path": str(study_blueprint_path)})

    adapter_catalog_path = output_dir / "adapter_catalog.json"
    adapter_catalog_path.write_text(json.dumps(adapter_catalog(include_availability=True), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("adapter_catalog_written", {"path": str(adapter_catalog_path)})

    runtime_planning_path = output_dir / "runtime_profile_planning.json"
    runtime_planning_path.write_text(json.dumps(export_runtime_profile(agent_spec.planning_runtime_profile), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    runtime_editing_path = output_dir / "runtime_profile_editing.json"
    runtime_editing_path.write_text(json.dumps(export_runtime_profile(agent_spec.editing_runtime_profile), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("runtime_profiles_written", {"planning": str(runtime_planning_path), "editing": str(runtime_editing_path)})

    case = materialize_panel_case(panel_spec)
    ledger.append("case_materialized", {"dataset_id": case.metadata.get("dataset_id", panel_spec.dataset), "n_units": len(case.units), "n_periods": len(case.times)})

    context_pack = pack_panel_case(case, artifacts_dir, budget=budget)
    context_pack_path = output_dir / "context_pack.json"
    context_pack.to_json(context_pack_path, pretty=True)
    ledger.append("context_pack_written", {"path": str(context_pack_path), "approx_tokens": context_pack.token_estimate.get("approx_tokens")})

    model = materialize_panel_model(panel_spec)
    config = PanelProtocolConfig(
        run_space_placebo=True,
        run_time_placebo=True,
        placebo_pre_rmspe_factor=panel_spec.placebo_pre_rmspe_factor,
        min_pre_periods=panel_spec.min_pre_periods,
        max_time_placebos=panel_spec.max_time_placebos,
    )
    report = benchmark_panel(case, model, config=config)
    ledger.append("benchmark_completed", {"model": getattr(model, "name", model.__class__.__name__), "ratio": report.metrics.get("post_pre_rmspe_ratio")})

    run_digest = pack_panel_run(case, report, artifacts_dir, budget=budget, run_id=run_id)
    run_digest_path = output_dir / "run_digest.json"
    run_digest.to_json(run_digest_path, pretty=True)
    ledger.append("run_digest_written", {"path": str(run_digest_path), "approx_tokens": run_digest.token_estimate.get("approx_tokens")})

    report_path = output_dir / "panel_report.md"
    report_path.write_text(render_panel_markdown(case, report), encoding="utf-8")
    ledger.append("markdown_report_written", {"path": str(report_path)})

    repo_map_path = None
    if include_repo_map:
        root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
        repo_map_text = build_repo_map_text(root, query="panel synthetic control placebo agent benchmark adapters runtime", max_files=18)
        repo_map_path = output_dir / "repo_map.txt"
        repo_map_path.write_text(repo_map_text, encoding="utf-8")
        ledger.append("repo_map_written", {"path": str(repo_map_path)})

    manifest = {
        "schema_version": "0.6.0",
        "run_id": run_id,
        "files": {
            "agent_spec": str(agent_spec_path),
            "study_blueprint": str(study_blueprint_path),
            "adapter_catalog": str(adapter_catalog_path),
            "runtime_profile_planning": str(runtime_planning_path),
            "runtime_profile_editing": str(runtime_editing_path),
            "context_pack": str(context_pack_path),
            "run_digest": str(run_digest_path),
            "panel_report": str(report_path),
            "run_ledger": str(output_dir / "run_ledger.jsonl"),
            "repo_map": str(repo_map_path) if repo_map_path is not None else None,
        },
        "artifacts": {
            "context_pack": [a.to_dict() for a in context_pack.artifact_refs],
            "run_digest": [a.to_dict() for a in run_digest.artifact_refs],
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("manifest_written", {"path": str(manifest_path)})

    triage_plan_path = output_dir / "context_plan_triage.json"
    analysis_plan_path = output_dir / "context_plan_analysis.json"
    editing_plan_path = output_dir / "context_plan_editing.json"
    triage_plan_path.write_text(json.dumps(build_context_plan(str(manifest_path), phase="triage", max_tokens=2600), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    analysis_plan_path.write_text(json.dumps(build_context_plan(str(manifest_path), phase="analysis", max_tokens=3200), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    editing_plan_path.write_text(json.dumps(build_context_plan(str(manifest_path), phase="editing", max_tokens=2400), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("context_plans_written", {"triage": str(triage_plan_path), "analysis": str(analysis_plan_path), "editing": str(editing_plan_path)})

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    refs = iter_artifact_refs(manifest_payload)
    context_tokens = int(context_pack.token_estimate.get("approx_tokens", 0))
    digest_tokens = int(run_digest.token_estimate.get("approx_tokens", 0))
    total_artifact_tokens = int(sum(ref.approx_tokens for ref in refs))
    summary_tokens = context_tokens + digest_tokens
    stats = {
        "schema_version": "0.6.0",
        "run_id": run_id,
        "context_pack_tokens": context_tokens,
        "run_digest_tokens": digest_tokens,
        "summary_tokens_total": summary_tokens,
        "artifact_tokens_total": total_artifact_tokens,
        "summary_vs_artifacts_ratio": float(summary_tokens / max(total_artifact_tokens, 1)),
        "triage_plan_tokens": json.loads(triage_plan_path.read_text(encoding="utf-8")).get("selected_tokens"),
        "analysis_plan_tokens": json.loads(analysis_plan_path.read_text(encoding="utf-8")).get("selected_tokens"),
        "editing_plan_tokens": json.loads(editing_plan_path.read_text(encoding="utf-8")).get("selected_tokens"),
        "planning_runtime_profile": agent_spec.planning_runtime_profile,
        "editing_runtime_profile": agent_spec.editing_runtime_profile,
        "candidate_adapter_count": len(agent_spec.candidate_adapters),
    }
    stats_path = output_dir / "bundle_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("bundle_stats_written", {"path": str(stats_path), "summary_vs_artifacts_ratio": stats["summary_vs_artifacts_ratio"]})

    manifest_payload["files"].update(
        {
            "context_plan_triage": str(triage_plan_path),
            "context_plan_analysis": str(analysis_plan_path),
            "context_plan_editing": str(editing_plan_path),
            "bundle_stats": str(stats_path),
        }
    )
    manifest_payload["summary"] = summarize_manifest(manifest_payload)
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    ledger.append("manifest_updated", {"path": str(manifest_path)})
    ledger.append("bundle_completed", {"manifest": str(manifest_path)})

    return PanelAgentBundle(
        run_id=run_id,
        root_dir=str(output_dir),
        manifest_path=str(manifest_path),
        context_pack_path=str(context_pack_path),
        run_digest_path=str(run_digest_path),
        report_path=str(report_path),
        ledger_path=str(output_dir / "run_ledger.jsonl"),
        triage_plan_path=str(triage_plan_path),
        analysis_plan_path=str(analysis_plan_path),
        editing_plan_path=str(editing_plan_path),
        stats_path=str(stats_path),
        study_blueprint_path=str(study_blueprint_path),
        adapter_catalog_path=str(adapter_catalog_path),
        runtime_planning_path=str(runtime_planning_path),
        runtime_editing_path=str(runtime_editing_path),
    )
