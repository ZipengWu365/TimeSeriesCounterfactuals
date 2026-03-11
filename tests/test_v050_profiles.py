import json
from pathlib import Path

from tscfbench.agent import export_runtime_profile, runtime_profile_catalog
from tscfbench.integrations import adapter_catalog, recommend_adapter_stack
from tscfbench.study import build_research_study_blueprint
from tscfbench import AgentResearchTaskSpec, TokenBudget, build_panel_agent_bundle


def test_adapter_catalog_smoke():
    rows = adapter_catalog(include_availability=True)
    ids = {row["id"] for row in rows}
    assert {"simple_scm_builtin", "pysyncon", "tfp_causalimpact", "statsforecast_cf"}.issubset(ids)


def test_recommend_stack_panel_smoke():
    rows = recommend_adapter_stack(task_family="panel", goal="research", token_aware=True, max_adapters=4)
    assert len(rows) == 4
    assert rows[0]["id"] in {"simple_scm_builtin", "did_builtin", "pysyncon", "scpi"}


def test_runtime_profile_export_smoke():
    planning = export_runtime_profile("openai_responses_planning_research_v1")
    assert planning["profile"]["api_family"] == "responses"
    assert planning["request_template"]["tool_choice"]["type"] == "allowed_tools"

    editing = export_runtime_profile("openai_chat_edit_patch_v1")
    assert editing["profile"]["api_family"] == "chat_completions"
    assert editing["request_template"]["prediction"]["type"] == "content"


def test_study_blueprint_smoke():
    spec = AgentResearchTaskSpec(task_family="panel")
    blueprint = build_research_study_blueprint(spec, max_adapters=5)
    assert blueprint.primary_task == "panel"
    assert len(blueprint.candidate_adapters) == 5
    assert "planning" in blueprint.runtime_profiles


def test_bundle_contains_v050_files(tmp_path: Path):
    spec = AgentResearchTaskSpec(
        dataset="synthetic_latent_factor",
        model="simple_scm",
        seed=5,
        intervention_t=40,
        n_units=8,
        n_periods=80,
        token_budget=TokenBudget(input_limit=3200, reserve_for_output=600, reserve_for_instructions=500),
    )
    bundle = build_panel_agent_bundle(spec, output_dir=tmp_path / "bundle", include_repo_map=False)
    manifest = json.loads(Path(bundle.manifest_path).read_text(encoding="utf-8"))
    assert Path(bundle.study_blueprint_path).exists()
    assert Path(bundle.adapter_catalog_path).exists()
    assert Path(bundle.runtime_planning_path).exists()
    assert Path(bundle.runtime_editing_path).exists()
    assert manifest["files"]["study_blueprint"].endswith("study_blueprint.json")
