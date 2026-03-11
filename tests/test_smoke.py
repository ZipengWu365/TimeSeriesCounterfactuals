import json
from pathlib import Path

from tscfbench import AgentResearchTaskSpec, TokenBudget, build_panel_agent_bundle, build_repo_map_text
from tscfbench.bench import benchmark
from tscfbench.datasets import list_dataset_cards
from tscfbench.datasets.synthetic import make_arma_impact, make_panel_latent_factor
from tscfbench.experiments import PanelExperimentSpec, run_panel_experiment
from tscfbench.models.did import DifferenceInDifferences
from tscfbench.models.ols import OLSImpact
from tscfbench.models.synthetic_control import SimpleSyntheticControl
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel


def test_impact_smoke():
    case = make_arma_impact(T=120, intervention_t=80, seed=1)
    out = benchmark(case, OLSImpact(add_trend=True))
    assert "rmse" in out.metrics
    assert out.metrics["rmse"] >= 0


def test_panel_protocol_smoke():
    case = make_panel_latent_factor(T=80, N=8, intervention_t=50, seed=1)
    report = benchmark_panel(
        case,
        SimpleSyntheticControl(),
        config=PanelProtocolConfig(
            run_space_placebo=True,
            run_time_placebo=True,
            placebo_pre_rmspe_factor=10.0,
            min_pre_periods=8,
            max_time_placebos=4,
        ),
    )
    assert "post_pre_rmspe_ratio" in report.metrics
    assert report.space_placebos.shape[0] == 7
    assert report.time_placebos.shape[0] > 0


def test_did_baseline_runs():
    case = make_panel_latent_factor(T=80, N=8, intervention_t=50, seed=2)
    report = benchmark_panel(case, DifferenceInDifferences())
    assert report.metrics["pre_rmspe"] >= 0


def test_experiment_runs():
    spec = PanelExperimentSpec()
    report = run_panel_experiment(spec)
    assert report.metrics["n_units"] == 12.0


def test_dataset_cards():
    cards = list_dataset_cards()
    assert {c.id for c in cards} >= {"german_reunification", "california_prop99", "basque_country"}


def test_agent_bundle_smoke(tmp_path: Path):
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
    bundle = build_panel_agent_bundle(spec, output_dir=tmp_path / "bundle", include_repo_map=True, repo_root=Path(__file__).resolve().parents[1])
    manifest = json.loads(Path(bundle.manifest_path).read_text(encoding="utf-8"))
    assert Path(bundle.context_pack_path).exists()
    assert Path(bundle.run_digest_path).exists()
    assert Path(bundle.ledger_path).exists()
    assert manifest["run_id"] == bundle.run_id


def test_repo_map_smoke():
    text = build_repo_map_text(Path(__file__).resolve().parents[1], query="synthetic control placebo", max_files=8)
    assert "SimpleSyntheticControl" in text
