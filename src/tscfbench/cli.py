from __future__ import annotations

import argparse
import json
from pathlib import Path

from tscfbench.agent import (
    AgentResearchTaskSpec,
    TokenBudget,
    build_context_plan,
    build_panel_agent_bundle,
    build_repo_map,
    build_repo_map_text,
    export_openai_function_tools,
    list_tool_profiles,
    export_runtime_profile,
    invoke_tool,
    list_artifacts,
    list_runtime_profiles,
    preview_tabular_artifact,
    read_text_artifact,
    render_agents_md,
    render_local_tscfbench_mcp_config,
    render_openai_docs_mcp_config,
    runtime_profile_catalog,
    search_text_artifact,
    summarize_manifest,
)
from tscfbench.agent.mcp_server import main as mcp_main
from tscfbench.agent.tokens import estimate_json_tokens, estimate_text_tokens
from tscfbench.bench import benchmark
from tscfbench.canonical import (
    CanonicalBenchmarkSpec,
    list_canonical_studies,
    render_canonical_markdown,
    run_canonical_benchmark,
)
from tscfbench.datasets import (
    list_dataset_cards,
    load_coingecko_market_chart,
    load_fred_series,
    load_github_star_history,
    to_log_returns,
)
from tscfbench.datasets.synthetic import make_arma_impact, make_panel_latent_factor
from tscfbench.experiments import PanelExperimentSpec, materialize_panel_case, run_panel_experiment
from tscfbench.install_matrix import install_matrix_json, render_install_matrix_markdown
from tscfbench.integrations.cards import adapter_catalog, recommend_adapter_stack
from tscfbench.models.ols import OLSImpact
from tscfbench.models.synthetic_control import SimpleSyntheticControl
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel
from tscfbench.report import render_panel_markdown
from tscfbench.study import build_research_study_blueprint
from tscfbench.sweeps import SweepMatrixSpec, make_default_sweep_spec, make_default_sweep_spec as _make_default_sweep_spec, render_sweep_markdown, run_sweep
from tscfbench.canonical import make_canonical_sweep_spec
from tscfbench.model_zoo import list_model_ids
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
from tscfbench.onramp import (
    doctor_report,
    essential_commands,
    render_doctor_markdown,
    render_essential_commands_markdown,
    render_tool_profiles_markdown,
    run_quickstart,
    tool_profile_notes,
)

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
from tscfbench.demo_cases import demo_catalog, render_demo_gallery_markdown, run_demo
from tscfbench.csv_runner import run_csv_impact, run_csv_panel
from tscfbench.share_packages import make_share_package_for_demo



def _write_or_print_text(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text)


def _write_or_print_json(payload: object, output: str | None) -> None:
    rendered = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


def _write_or_print_df(df, output: str | None, *, fmt: str = "json") -> None:
    fmt = str(fmt or "json").lower()
    if fmt == "csv":
        rendered = df.to_csv(index=False)
    else:
        rendered = json.dumps(df.to_dict(orient="records"), indent=2, ensure_ascii=False, default=str)
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


def _cmd_intro(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(package_overview(), args.output)
    else:
        _write_or_print_text(render_package_overview_markdown(), args.output)
    return 0


def _cmd_api_handbook(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(api_handbook(), args.output)
    else:
        _write_or_print_text(render_api_handbook_markdown(), args.output)
    return 0


def _cmd_use_cases(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(use_case_catalog(), args.output)
    else:
        _write_or_print_text(render_use_cases_markdown(), args.output)
    return 0


def _cmd_environments(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(environment_profiles(), args.output)
    else:
        _write_or_print_text(render_environment_profiles_markdown(), args.output)
    return 0


def _cmd_cli_guide(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(cli_guide(), args.output)
    else:
        _write_or_print_text(render_cli_guide_markdown(), args.output)
    return 0


def _cmd_package_story(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(package_story(), args.output)
    else:
        _write_or_print_text(render_package_story_markdown(), args.output)
    return 0


def _cmd_capability_map(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(capability_map(), args.output)
    else:
        _write_or_print_text(render_capability_map_markdown(), args.output)
    return 0


def _cmd_api_atlas(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(api_atlas(), args.output)
    else:
        _write_or_print_text(render_api_atlas_markdown(), args.output)
    return 0


def _cmd_scenario_matrix(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(scenario_matrix(), args.output)
    else:
        _write_or_print_text(render_scenario_matrix_markdown(), args.output)
    return 0


def _cmd_tutorial_index(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(tutorial_index(), args.output)
    else:
        _write_or_print_text(render_tutorial_index_markdown(), args.output)
    return 0


def _cmd_high_traffic_cases(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(high_traffic_cases(), args.output)
    else:
        _write_or_print_text(render_high_traffic_cases_markdown(), args.output)
    return 0


def _cmd_public_data_sources(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(public_data_sources(), args.output)
    else:
        _write_or_print_text(render_public_data_sources_markdown(), args.output)
    return 0


def _cmd_make_release_kit(args: argparse.Namespace) -> int:
    payload = write_release_kit(args.output)
    _write_or_print_json(payload, None)
    return 0


def _cmd_ecosystem_audit(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(ecosystem_audit(), args.output)
    else:
        _write_or_print_text(render_ecosystem_audit_markdown(), args.output)
    return 0


def _cmd_feature_coverage(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(feature_coverage_matrix(), args.output)
    else:
        _write_or_print_text(render_feature_coverage_markdown(), args.output)
    return 0


def _cmd_differentiators(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(package_differentiators(), args.output)
    else:
        _write_or_print_text(render_differentiators_markdown(), args.output)
    return 0


def _cmd_github_readme(args: argparse.Namespace) -> int:
    _write_or_print_text(render_github_readme_markdown(), args.output)
    return 0


def _cmd_website_home(args: argparse.Namespace) -> int:
    _write_or_print_text(render_docs_homepage_markdown(), args.output)
    return 0


def _cmd_agent_first_design(args: argparse.Namespace) -> int:
    _write_or_print_text(render_agent_first_design_markdown(), args.output)
    return 0


def _cmd_make_positioning_assets(args: argparse.Namespace) -> int:
    payload = write_positioning_assets(args.output)
    _write_or_print_json(payload, None)
    return 0


def _cmd_fetch_github_stars(args: argparse.Namespace) -> int:
    df = load_github_star_history(args.owner, args.repo, token=args.token, max_pages=args.max_pages)
    _write_or_print_df(df, args.output, fmt=args.format)
    return 0


def _cmd_fetch_coingecko(args: argparse.Namespace) -> int:
    df = load_coingecko_market_chart(
        args.coin_id,
        vs_currency=args.vs_currency,
        days=args.days,
        interval=args.interval,
        api_key=args.api_key,
    )
    if args.as_returns:
        df = to_log_returns(df, value_col="price", out_col="log_return")
    _write_or_print_df(df, args.output, fmt=args.format)
    return 0


def _cmd_fetch_fred(args: argparse.Namespace) -> int:
    df = load_fred_series(args.series_id)
    if args.as_returns:
        df = to_log_returns(df, value_col="value", out_col="log_return")
    _write_or_print_df(df, args.output, fmt=args.format)
    return 0


def _cmd_start_here(args: argparse.Namespace) -> int:
    kwargs = {
        "persona": args.persona,
        "task_family": args.task_family,
        "environment": args.environment,
        "goal": args.goal,
        "need_agents": True if args.need_agents else (False if args.no_agents else None),
    }
    if args.format == "json":
        _write_or_print_json(recommend_start_path(**kwargs), args.output)
    else:
        _write_or_print_text(render_start_here_markdown(**kwargs), args.output)
    return 0


def _cmd_quickstart(args: argparse.Namespace) -> int:
    payload = run_quickstart(
        args.output,
        data_source=args.data_source,
        include_external=args.include_external,
        seed=args.seed,
        plot=not args.no_plot,
    )
    _write_or_print_json(payload, None)
    return 0



def _cmd_doctor(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(doctor_report(), args.output)
    else:
        _write_or_print_text(render_doctor_markdown(), args.output)
    return 0



def _cmd_essentials(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(essential_commands(), args.output)
    else:
        _write_or_print_text(render_essential_commands_markdown(), args.output)
    return 0



def _cmd_list_tool_profiles(args: argparse.Namespace) -> int:
    payload = tool_profile_notes()
    if args.format == "markdown":
        _write_or_print_text(render_tool_profiles_markdown(), args.output)
    else:
        _write_or_print_json(payload, args.output)
    return 0


def _cmd_workflow_recipes(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(workflow_recipes(), args.output)
    else:
        _write_or_print_text(render_workflow_recipes_markdown(), args.output)
    return 0


def _cmd_benchmark_cards(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(benchmark_cards(), args.output)
    else:
        _write_or_print_text(render_benchmark_cards_markdown(), args.output)
    return 0


def _cmd_recommend_path(args: argparse.Namespace) -> int:
    payload = recommend_start_path(
        persona=args.persona,
        task_family=args.task_family,
        environment=args.environment,
        goal=args.goal,
        need_agents=True if args.need_agents else (False if args.no_agents else None),
        top_k=args.top_k,
    )
    if args.format == "markdown":
        _write_or_print_text(render_start_here_markdown(
            persona=args.persona,
            task_family=args.task_family,
            environment=args.environment,
            goal=args.goal,
            need_agents=True if args.need_agents else (False if args.no_agents else None),
        ), args.output)
    else:
        _write_or_print_json(payload, args.output)
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    if args.demo_id:
        payload = run_demo(args.demo_id, output_dir=args.output, plot=not args.no_plot)
        if getattr(args, "share_package", False):
            share_dir = Path(args.output) / f"{args.demo_id}_share_package"
            share_payload = make_share_package_for_demo(args.demo_id, output_dir=share_dir, plot=not args.no_plot)
            payload["share_package"] = share_payload
        _write_or_print_json(payload, None)
        return 0

    impact = make_arma_impact(T=200, intervention_t=140, seed=7)
    ols = OLSImpact(add_trend=True)
    out1 = benchmark(impact, ols)

    panel = make_panel_latent_factor(T=120, N=12, intervention_t=70, seed=7)
    scm = SimpleSyntheticControl()
    report = benchmark_panel(
        panel,
        scm,
        config=PanelProtocolConfig(
            run_space_placebo=True,
            run_time_placebo=True,
            placebo_pre_rmspe_factor=5.0,
            min_pre_periods=12,
            max_time_placebos=8,
        ),
    )

    payload = {
        "impact_case": out1.metrics,
        "panel_case": report.metrics,
        "space_placebos_head": report.space_placebos.head(5).to_dict(orient="records"),
        "time_placebos_head": report.time_placebos.head(5).to_dict(orient="records"),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


def _cmd_make_share_package(args: argparse.Namespace) -> int:
    payload = make_share_package_for_demo(
        args.demo_id,
        output_dir=args.output,
        plot=not args.no_plot,
    )
    _write_or_print_json(payload, None)
    return 0


def _cmd_demo_gallery(args: argparse.Namespace) -> int:
    if args.format == "json":
        _write_or_print_json(demo_catalog(), args.output)
    else:
        _write_or_print_text(render_demo_gallery_markdown(), args.output)
    return 0


def _cmd_run_csv_panel(args: argparse.Namespace) -> int:
    payload = run_csv_panel(
        args.csv_path,
        unit_col=args.unit_col,
        time_col=args.time_col,
        y_col=args.y_col,
        treated_unit=args.treated_unit,
        intervention_t=args.intervention_t,
        model=args.model,
        output_dir=args.output,
        plot=not args.no_plot,
        title=args.title,
    )
    _write_or_print_json(payload, None)
    return 0


def _cmd_run_csv_impact(args: argparse.Namespace) -> int:
    x_cols = [c for c in (args.x_cols or []) if c]
    payload = run_csv_impact(
        args.csv_path,
        time_col=args.time_col,
        y_col=args.y_col,
        x_cols=x_cols,
        intervention_t=args.intervention_t,
        model=args.model,
        output_dir=args.output,
        plot=not args.no_plot,
        title=args.title,
    )
    _write_or_print_json(payload, None)
    return 0


def _cmd_datasets(_: argparse.Namespace) -> int:
    cards = [
        {
            "id": c.id,
            "task_type": c.task_type,
            "title": c.title,
            "treated_unit": c.treated_unit,
            "intervention_t": c.intervention_t,
            "outcome": c.outcome,
            "summary": c.summary,
            "source": c.source,
            "snapshot_available": c.snapshot_available,
            "remote_available": c.remote_available,
        }
        for c in list_dataset_cards()
    ]
    print(json.dumps(cards, indent=2, ensure_ascii=False))
    return 0


def _cmd_install_matrix(args: argparse.Namespace) -> int:
    if args.format == "markdown":
        text = render_install_matrix_markdown()
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text)
    else:
        payload = install_matrix_json()
        if args.output:
            Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_list_canonical_studies(_: argparse.Namespace) -> int:
    payload = [s.to_dict() for s in list_canonical_studies()]
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_make_canonical_spec(args: argparse.Namespace) -> int:
    study_ids = args.study_ids if args.study_ids else None
    models = args.models if args.models else None
    spec = CanonicalBenchmarkSpec(
        name=args.name,
        study_ids=list(study_ids) if study_ids is not None else [s.id for s in list_canonical_studies()],
        models=list(models) if models is not None else None,
        include_external=bool(args.include_external and not args.no_external),
        data_source=args.data_source,
        seed=args.seed,
        stop_on_error=args.stop_on_error,
    )
    if args.output:
        spec.to_json(args.output)
    else:
        print(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_run_canonical(args: argparse.Namespace) -> int:
    spec = CanonicalBenchmarkSpec.from_json(args.spec)
    run = run_canonical_benchmark(spec)
    payload = {"summary": run.summary(), "results": run.to_frame().to_dict(orient="records")}
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


def _cmd_render_canonical_report(args: argparse.Namespace) -> int:
    spec = CanonicalBenchmarkSpec.from_json(args.spec)
    run = run_canonical_benchmark(spec)
    md = render_canonical_markdown(run)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0


def _cmd_list_adapters(args: argparse.Namespace) -> int:
    rows = adapter_catalog(include_availability=True)
    if args.task_family:
        rows = [row for row in rows if row["task_family"] == args.task_family or (args.task_family == "panel" and row["task_family"] == "quasi_experiment")]
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


def _cmd_recommend_stack(args: argparse.Namespace) -> int:
    payload = recommend_adapter_stack(task_family=args.task_family, goal=args.goal, token_aware=not args.no_token_aware, max_adapters=args.max_adapters)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_list_model_ids(args: argparse.Namespace) -> int:
    print(json.dumps({"model_ids": list_model_ids(task_family=args.task_family)}, indent=2, ensure_ascii=False))
    return 0


def _cmd_make_sweep_spec(args: argparse.Namespace) -> int:
    spec = make_default_sweep_spec(task_family=args.task_family, include_external=bool(args.include_external and not args.no_external), seed=args.seed, data_source=args.data_source)
    if args.output:
        spec.to_json(args.output)
    else:
        print(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_run_sweep(args: argparse.Namespace) -> int:
    spec = SweepMatrixSpec.from_json(args.spec)
    run = run_sweep(spec)
    payload = {"summary": run.summary(), "results": run.to_frame().to_dict(orient="records")}
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


def _cmd_render_sweep_report(args: argparse.Namespace) -> int:
    spec = SweepMatrixSpec.from_json(args.spec)
    run = run_sweep(spec)
    md = render_sweep_markdown(run)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0


def _cmd_list_runtime_profiles(_: argparse.Namespace) -> int:
    print(json.dumps({"profiles": runtime_profile_catalog(), "usage_hint": "You can export by alias too: default, planning, analysis, editing."}, indent=2, ensure_ascii=False))
    return 0


def _cmd_export_runtime_profile(args: argparse.Namespace) -> int:
    payload = export_runtime_profile(args.profile_id)
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_panel_spec(args: argparse.Namespace) -> int:
    spec = PanelExperimentSpec(
        dataset=args.dataset,
        model=args.model,
        seed=args.seed,
        intervention_t=args.intervention_t,
        n_units=args.n_units,
        n_periods=args.n_periods,
        placebo_pre_rmspe_factor=args.placebo_pre_rmspe_factor,
        min_pre_periods=args.min_pre_periods,
        max_time_placebos=args.max_time_placebos,
        data_source=args.data_source,
        model_kwargs=json.loads(args.model_kwargs_json) if args.model_kwargs_json else {},
    )
    if args.output:
        spec.to_json(args.output)
    else:
        print(json.dumps(spec.__dict__, indent=2, ensure_ascii=False))
    return 0


def _cmd_run_panel_spec(args: argparse.Namespace) -> int:
    spec = PanelExperimentSpec.from_json(args.spec)
    report = run_panel_experiment(spec)
    payload = {
        "metrics": report.metrics,
        "space_placebos_head": report.space_placebos.head(8).to_dict(orient="records"),
        "time_placebos_head": report.time_placebos.head(8).to_dict(orient="records"),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    return 0


def _cmd_render_panel_report(args: argparse.Namespace) -> int:
    spec = PanelExperimentSpec.from_json(args.spec)
    case = materialize_panel_case(spec)
    report = run_panel_experiment(spec)
    md = render_panel_markdown(case, report)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0


def _cmd_make_agent_spec(args: argparse.Namespace) -> int:
    spec = AgentResearchTaskSpec(
        task_family=args.task_family,
        dataset=args.dataset,
        model=args.model,
        seed=args.seed,
        intervention_t=args.intervention_t,
        n_units=args.n_units,
        n_periods=args.n_periods,
        placebo_pre_rmspe_factor=args.placebo_pre_rmspe_factor,
        min_pre_periods=args.min_pre_periods,
        max_time_placebos=args.max_time_placebos,
        token_budget=TokenBudget(input_limit=args.input_limit, reserve_for_output=args.reserve_for_output, reserve_for_instructions=args.reserve_for_instructions),
    )
    if args.output:
        spec.to_json(args.output, pretty=True)
    else:
        print(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_make_study_blueprint(args: argparse.Namespace) -> int:
    spec = AgentResearchTaskSpec.from_json(args.spec)
    blueprint = build_research_study_blueprint(spec, max_adapters=args.max_adapters)
    if args.output:
        blueprint.to_json(args.output, pretty=True)
    else:
        print(json.dumps(blueprint.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_build_agent_bundle(args: argparse.Namespace) -> int:
    spec = AgentResearchTaskSpec.from_json(args.spec)
    bundle = build_panel_agent_bundle(spec, output_dir=args.output, include_repo_map=not args.no_repo_map, repo_root=args.repo_root)
    print(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_repo_map(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if args.json:
        payload = [e.to_dict() for e in build_repo_map(root, query=args.query, max_files=args.max_files, include_tests=args.include_tests)]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(build_repo_map_text(root, query=args.query, max_files=args.max_files, include_tests=args.include_tests))
    return 0


def _cmd_write_agents_md(args: argparse.Namespace) -> int:
    text = render_agents_md(project_name=args.project_name)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _cmd_write_openai_docs_mcp(args: argparse.Namespace) -> int:
    payload = render_openai_docs_mcp_config(client=args.client)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_write_local_mcp(args: argparse.Namespace) -> int:
    payload = render_local_tscfbench_mcp_config(client=args.client, server_name=args.server_name, command=args.command, args=args.args)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_estimate_tokens(args: argparse.Namespace) -> int:
    candidate_path = args.path or args.target
    text = args.text or ""
    source = "text"
    if candidate_path:
        possible = Path(candidate_path)
        if possible.exists() and possible.is_file():
            text = possible.read_text(encoding="utf-8")
            source = str(possible)
        elif args.text is None:
            text = str(candidate_path)
    payload = {
        "source": source,
        "text_tokens": estimate_text_tokens(text).to_dict(),
        "json_tokens": estimate_json_tokens({"text": text}).to_dict(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_list_artifacts(args: argparse.Namespace) -> int:
    payload = {"manifest_summary": summarize_manifest(args.manifest), "artifacts": list_artifacts(args.manifest)}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_read_artifact(args: argparse.Namespace) -> int:
    payload = read_text_artifact(args.manifest, artifact_id=args.id, kind=args.kind, path=args.path, offset_chars=args.offset_chars, max_chars=args.max_chars)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_search_artifact(args: argparse.Namespace) -> int:
    payload = search_text_artifact(args.manifest, artifact_id=args.id, kind=args.kind, path=args.path, query=args.query, max_hits=args.max_hits)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_preview_artifact_table(args: argparse.Namespace) -> int:
    payload = preview_tabular_artifact(args.manifest, artifact_id=args.id, kind=args.kind, path=args.path, rows=args.rows, columns=args.columns)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_plan_context(args: argparse.Namespace) -> int:
    payload = build_context_plan(args.manifest, phase=args.phase, max_tokens=args.max_tokens, query=args.query, include_repo_map=not args.no_repo_map)
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_export_openai_tools(args: argparse.Namespace) -> int:
    payload = export_openai_function_tools(strict=not args.non_strict, profile=args.profile)
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_invoke_tool(args: argparse.Namespace) -> int:
    tool_input = json.loads(args.input_json) if args.input_json else {}
    payload = invoke_tool(args.name, tool_input, repo_root=Path(args.repo_root) if args.repo_root else None)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _cmd_mcp_server(_: argparse.Namespace) -> int:
    return mcp_main()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tscfbench", description="Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff", epilog="Run `python -m tscfbench essentials` for the narrow command set or `python -m tscfbench --help` for the full CLI.")
    sub = p.add_subparsers(dest="cmd", required=False)

    demo = sub.add_parser("demo")
    demo.add_argument("demo_id", nargs="?", default=None)
    demo.add_argument("-o", "--output", default="tscfbench_demo")
    demo.add_argument("--no-plot", action="store_true")
    demo.add_argument("--share-package", action="store_true")
    demo.set_defaults(func=_cmd_demo)

    msp = sub.add_parser("make-share-package")
    msp.add_argument("--demo-id", required=True)
    msp.add_argument("-o", "--output", default="tscfbench_share_package")
    msp.add_argument("--no-plot", action="store_true")
    msp.set_defaults(func=_cmd_make_share_package)

    dg = sub.add_parser("demo-gallery")
    dg.add_argument("--format", choices=["markdown", "json"], default="markdown")
    dg.add_argument("-o", "--output", default=None)
    dg.set_defaults(func=_cmd_demo_gallery)

    intro = sub.add_parser("intro")
    intro.add_argument("--format", choices=["markdown", "json"], default="markdown")
    intro.add_argument("-o", "--output", default=None)
    intro.set_defaults(func=_cmd_intro)

    ps = sub.add_parser("package-story")
    ps.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ps.add_argument("-o", "--output", default=None)
    ps.set_defaults(func=_cmd_package_story)

    cm = sub.add_parser("capability-map")
    cm.add_argument("--format", choices=["markdown", "json"], default="markdown")
    cm.add_argument("-o", "--output", default=None)
    cm.set_defaults(func=_cmd_capability_map)

    aa = sub.add_parser("api-atlas")
    aa.add_argument("--format", choices=["markdown", "json"], default="markdown")
    aa.add_argument("-o", "--output", default=None)
    aa.set_defaults(func=_cmd_api_atlas)

    sm = sub.add_parser("scenario-matrix")
    sm.add_argument("--format", choices=["markdown", "json"], default="markdown")
    sm.add_argument("-o", "--output", default=None)
    sm.set_defaults(func=_cmd_scenario_matrix)

    ti = sub.add_parser("tutorial-index")
    ti.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ti.add_argument("-o", "--output", default=None)
    ti.set_defaults(func=_cmd_tutorial_index)

    ah = sub.add_parser("api-handbook")
    ah.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ah.add_argument("-o", "--output", default=None)
    ah.set_defaults(func=_cmd_api_handbook)

    uc = sub.add_parser("use-cases")
    uc.add_argument("--format", choices=["markdown", "json"], default="markdown")
    uc.add_argument("-o", "--output", default=None)
    uc.set_defaults(func=_cmd_use_cases)

    env = sub.add_parser("environments")
    env.add_argument("--format", choices=["markdown", "json"], default="markdown")
    env.add_argument("-o", "--output", default=None)
    env.set_defaults(func=_cmd_environments)

    cg = sub.add_parser("cli-guide")
    cg.add_argument("--format", choices=["markdown", "json"], default="markdown")
    cg.add_argument("-o", "--output", default=None)
    cg.set_defaults(func=_cmd_cli_guide)
    sh = sub.add_parser("start-here")
    sh.add_argument("--persona", default=None)
    sh.add_argument("--task-family", default=None)
    sh.add_argument("--environment", default=None)
    sh.add_argument("--goal", default=None)
    sh.add_argument("--need-agents", action="store_true")
    sh.add_argument("--no-agents", action="store_true")
    sh.add_argument("--format", choices=["markdown", "json"], default="markdown")
    sh.add_argument("-o", "--output", default=None)
    sh.set_defaults(func=_cmd_start_here)

    qs = sub.add_parser("quickstart")
    qs.add_argument("-o", "--output", default="tscfbench_quickstart")
    qs.add_argument("--data-source", choices=["snapshot", "auto", "remote"], default="snapshot")
    qs.add_argument("--include-external", action="store_true")
    qs.add_argument("--seed", type=int, default=7)
    qs.add_argument("--no-plot", action="store_true")
    qs.set_defaults(func=_cmd_quickstart)

    rcp = sub.add_parser("run-csv-panel")
    rcp.add_argument("csv_path")
    rcp.add_argument("--unit-col", required=True)
    rcp.add_argument("--time-col", required=True)
    rcp.add_argument("--y-col", required=True)
    rcp.add_argument("--treated-unit", required=True)
    rcp.add_argument("--intervention-t", required=True)
    rcp.add_argument("--model", default="simple_scm")
    rcp.add_argument("--title", default=None)
    rcp.add_argument("-o", "--output", default="tscfbench_csv_panel")
    rcp.add_argument("--no-plot", action="store_true")
    rcp.set_defaults(func=_cmd_run_csv_panel)

    rci = sub.add_parser("run-csv-impact")
    rci.add_argument("csv_path")
    rci.add_argument("--time-col", required=True)
    rci.add_argument("--y-col", required=True)
    rci.add_argument("--x-cols", nargs="*", default=[])
    rci.add_argument("--intervention-t", required=True)
    rci.add_argument("--model", default="ols_impact")
    rci.add_argument("--title", default=None)
    rci.add_argument("-o", "--output", default="tscfbench_csv_impact")
    rci.add_argument("--no-plot", action="store_true")
    rci.set_defaults(func=_cmd_run_csv_impact)

    doc = sub.add_parser("doctor")
    doc.add_argument("--format", choices=["markdown", "json"], default="markdown")
    doc.add_argument("-o", "--output", default=None)
    doc.set_defaults(func=_cmd_doctor)

    ess = sub.add_parser("essentials")
    ess.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ess.add_argument("-o", "--output", default=None)
    ess.set_defaults(func=_cmd_essentials)

    wr = sub.add_parser("workflow-recipes")
    wr.add_argument("--format", choices=["markdown", "json"], default="markdown")
    wr.add_argument("-o", "--output", default=None)
    wr.set_defaults(func=_cmd_workflow_recipes)

    bc = sub.add_parser("benchmark-cards")
    bc.add_argument("--format", choices=["markdown", "json"], default="markdown")
    bc.add_argument("-o", "--output", default=None)
    bc.set_defaults(func=_cmd_benchmark_cards)

    htc = sub.add_parser("high-traffic-cases")
    htc.add_argument("--format", choices=["markdown", "json"], default="markdown")
    htc.add_argument("-o", "--output", default=None)
    htc.set_defaults(func=_cmd_high_traffic_cases)

    pds = sub.add_parser("public-data-sources")
    pds.add_argument("--format", choices=["markdown", "json"], default="markdown")
    pds.add_argument("-o", "--output", default=None)
    pds.set_defaults(func=_cmd_public_data_sources)

    ea = sub.add_parser("ecosystem-audit")
    ea.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ea.add_argument("-o", "--output", default=None)
    ea.set_defaults(func=_cmd_ecosystem_audit)

    fc = sub.add_parser("feature-coverage")
    fc.add_argument("--format", choices=["markdown", "json"], default="markdown")
    fc.add_argument("-o", "--output", default=None)
    fc.set_defaults(func=_cmd_feature_coverage)

    diff = sub.add_parser("differentiators")
    diff.add_argument("--format", choices=["markdown", "json"], default="markdown")
    diff.add_argument("-o", "--output", default=None)
    diff.set_defaults(func=_cmd_differentiators)

    gr = sub.add_parser("github-readme")
    gr.add_argument("-o", "--output", default=None)
    gr.set_defaults(func=_cmd_github_readme)

    wh = sub.add_parser("website-home")
    wh.add_argument("-o", "--output", default=None)
    wh.set_defaults(func=_cmd_website_home)

    afd = sub.add_parser("agent-first-design")
    afd.add_argument("-o", "--output", default=None)
    afd.set_defaults(func=_cmd_agent_first_design)

    rp = sub.add_parser("recommend-path")
    rp.add_argument("--persona", default=None)
    rp.add_argument("--task-family", default=None)
    rp.add_argument("--environment", default=None)
    rp.add_argument("--goal", default=None)
    rp.add_argument("--need-agents", action="store_true")
    rp.add_argument("--no-agents", action="store_true")
    rp.add_argument("--top-k", type=int, default=3)
    rp.add_argument("--format", choices=["json", "markdown"], default="json")
    rp.add_argument("-o", "--output", default=None)
    rp.set_defaults(func=_cmd_recommend_path)
    mrk = sub.add_parser("make-release-kit")
    mrk.add_argument("-o", "--output", default="release_kit")
    mrk.set_defaults(func=_cmd_make_release_kit)

    mpa = sub.add_parser("make-positioning-assets")
    mpa.add_argument("-o", "--output", default="positioning_assets")
    mpa.set_defaults(func=_cmd_make_positioning_assets)

    fgs = sub.add_parser("fetch-github-stars")
    fgs.add_argument("owner")
    fgs.add_argument("repo")
    fgs.add_argument("--token", default=None)
    fgs.add_argument("--max-pages", type=int, default=None)
    fgs.add_argument("--format", choices=["json", "csv"], default="json")
    fgs.add_argument("-o", "--output", default=None)
    fgs.set_defaults(func=_cmd_fetch_github_stars)

    fcg = sub.add_parser("fetch-coingecko")
    fcg.add_argument("coin_id")
    fcg.add_argument("--vs-currency", default="usd")
    fcg.add_argument("--days", default="max")
    fcg.add_argument("--interval", default=None)
    fcg.add_argument("--api-key", default=None)
    fcg.add_argument("--as-returns", action="store_true")
    fcg.add_argument("--format", choices=["json", "csv"], default="json")
    fcg.add_argument("-o", "--output", default=None)
    fcg.set_defaults(func=_cmd_fetch_coingecko)

    ffred = sub.add_parser("fetch-fred")
    ffred.add_argument("series_id")
    ffred.add_argument("--as-returns", action="store_true")
    ffred.add_argument("--format", choices=["json", "csv"], default="json")
    ffred.add_argument("-o", "--output", default=None)
    ffred.set_defaults(func=_cmd_fetch_fred)

    sub.add_parser("datasets").set_defaults(func=_cmd_datasets)
    sub.add_parser("list-canonical-studies").set_defaults(func=_cmd_list_canonical_studies)

    im = sub.add_parser("install-matrix")
    im.add_argument("--format", choices=["json", "markdown"], default="json")
    im.add_argument("-o", "--output", default=None)
    im.set_defaults(func=_cmd_install_matrix)

    mcs = sub.add_parser("make-canonical-spec")
    mcs.add_argument("--name", default="canonical_panel_benchmark")
    mcs.add_argument("--study-ids", nargs="*", default=None)
    mcs.add_argument("--models", nargs="*", default=None)
    mcs.add_argument("--data-source", choices=["auto", "remote", "snapshot"], default="auto")
    mcs.add_argument("--seed", type=int, default=7)
    mcs.add_argument("--include-external", action="store_true")
    mcs.add_argument("--no-external", action="store_true")
    mcs.add_argument("--stop-on-error", action="store_true")
    mcs.add_argument("-o", "--output", default=None)
    mcs.set_defaults(func=_cmd_make_canonical_spec)

    rc = sub.add_parser("run-canonical")
    rc.add_argument("spec")
    rc.add_argument("-o", "--output", default=None)
    rc.set_defaults(func=_cmd_run_canonical)

    rcr = sub.add_parser("render-canonical-report")
    rcr.add_argument("spec")
    rcr.add_argument("-o", "--output", default=None)
    rcr.set_defaults(func=_cmd_render_canonical_report)

    lp = sub.add_parser("list-adapters")
    lp.add_argument("--task-family", default=None)
    lp.set_defaults(func=_cmd_list_adapters)

    rs = sub.add_parser("recommend-stack")
    rs.add_argument("--task-family", default="panel")
    rs.add_argument("--goal", default="research")
    rs.add_argument("--max-adapters", type=int, default=6)
    rs.add_argument("--no-token-aware", action="store_true")
    rs.set_defaults(func=_cmd_recommend_stack)

    lm = sub.add_parser("list-model-ids")
    lm.add_argument("--task-family", default=None)
    lm.set_defaults(func=_cmd_list_model_ids)

    mss = sub.add_parser("make-sweep-spec")
    mss.add_argument("--task-family", default="panel", choices=["panel", "impact"])
    mss.add_argument("--seed", type=int, default=7)
    mss.add_argument("--data-source", choices=["auto", "remote", "snapshot"], default="auto")
    mss.add_argument("--include-external", action="store_true")
    mss.add_argument("--no-external", action="store_true")
    mss.add_argument("-o", "--output", default=None)
    mss.set_defaults(func=_cmd_make_sweep_spec)

    rsw = sub.add_parser("run-sweep")
    rsw.add_argument("spec")
    rsw.add_argument("-o", "--output", default=None)
    rsw.set_defaults(func=_cmd_run_sweep)

    rsr = sub.add_parser("render-sweep-report")
    rsr.add_argument("spec")
    rsr.add_argument("-o", "--output", default=None)
    rsr.set_defaults(func=_cmd_render_sweep_report)

    sub.add_parser("list-runtime-profiles").set_defaults(func=_cmd_list_runtime_profiles)

    ltp = sub.add_parser("list-tool-profiles")
    ltp.add_argument("--format", choices=["json", "markdown"], default="json")
    ltp.add_argument("-o", "--output", default=None)
    ltp.set_defaults(func=_cmd_list_tool_profiles)

    erp = sub.add_parser("export-runtime-profile")
    erp.add_argument("profile_id")
    erp.add_argument("-o", "--output", default=None)
    erp.set_defaults(func=_cmd_export_runtime_profile)

    mps = sub.add_parser("make-panel-spec")
    mps.add_argument("--dataset", default="synthetic_latent_factor")
    mps.add_argument("--model", default="simple_scm")
    mps.add_argument("--seed", type=int, default=7)
    mps.add_argument("--intervention-t", type=int, default=70)
    mps.add_argument("--n-units", type=int, default=12)
    mps.add_argument("--n-periods", type=int, default=120)
    mps.add_argument("--data-source", choices=["auto", "remote", "snapshot"], default="auto")
    mps.add_argument("--placebo-pre-rmspe-factor", type=float, default=5.0)
    mps.add_argument("--min-pre-periods", type=int, default=12)
    mps.add_argument("--max-time-placebos", type=int, default=8)
    mps.add_argument("--model-kwargs-json", default=None)
    mps.add_argument("-o", "--output", default=None)
    mps.set_defaults(func=_cmd_panel_spec)

    rps = sub.add_parser("run-panel-spec")
    rps.add_argument("spec")
    rps.set_defaults(func=_cmd_run_panel_spec)

    rpr = sub.add_parser("render-panel-report")
    rpr.add_argument("spec")
    rpr.add_argument("-o", "--output", default=None)
    rpr.set_defaults(func=_cmd_render_panel_report)

    mas = sub.add_parser("make-agent-spec")
    mas.add_argument("--task-family", default="panel")
    mas.add_argument("--dataset", default="synthetic_latent_factor")
    mas.add_argument("--model", default="simple_scm")
    mas.add_argument("--seed", type=int, default=7)
    mas.add_argument("--intervention-t", type=int, default=70)
    mas.add_argument("--n-units", type=int, default=12)
    mas.add_argument("--n-periods", type=int, default=120)
    mas.add_argument("--placebo-pre-rmspe-factor", type=float, default=5.0)
    mas.add_argument("--min-pre-periods", type=int, default=12)
    mas.add_argument("--max-time-placebos", type=int, default=8)
    mas.add_argument("--input-limit", type=int, default=8000)
    mas.add_argument("--reserve-for-output", type=int, default=2000)
    mas.add_argument("--reserve-for-instructions", type=int, default=1000)
    mas.add_argument("-o", "--output", default=None)
    mas.set_defaults(func=_cmd_make_agent_spec)

    msb = sub.add_parser("make-study-blueprint")
    msb.add_argument("spec")
    msb.add_argument("--max-adapters", type=int, default=8)
    msb.add_argument("-o", "--output", default=None)
    msb.set_defaults(func=_cmd_make_study_blueprint)

    bab = sub.add_parser("build-agent-bundle")
    bab.add_argument("spec")
    bab.add_argument("-o", "--output", default="bundle_dir")
    bab.add_argument("--repo-root", default=None)
    bab.add_argument("--no-repo-map", action="store_true")
    bab.set_defaults(func=_cmd_build_agent_bundle)

    rm = sub.add_parser("repo-map")
    rm.add_argument("--root", default=".")
    rm.add_argument("--query", default=None)
    rm.add_argument("--max-files", type=int, default=12)
    rm.add_argument("--include-tests", action="store_true")
    rm.add_argument("--json", action="store_true")
    rm.set_defaults(func=_cmd_repo_map)

    wam = sub.add_parser("write-agents-md")
    wam.add_argument("--project-name", default="tscfbench")
    wam.add_argument("-o", "--output", default=None)
    wam.set_defaults(func=_cmd_write_agents_md)

    wod = sub.add_parser("write-openai-docs-mcp")
    wod.add_argument("--client", default="vscode", choices=["vscode", "cursor", "codex"])
    wod.add_argument("-o", "--output", default=None)
    wod.set_defaults(func=_cmd_write_openai_docs_mcp)

    wlm = sub.add_parser("write-local-mcp")
    wlm.add_argument("--client", default="vscode", choices=["vscode", "cursor", "codex"])
    wlm.add_argument("--server-name", default="tscfbench")
    wlm.add_argument("--command", default="tscfbench")
    wlm.add_argument("--args", nargs="*", default=["mcp-server"])
    wlm.add_argument("-o", "--output", default=None)
    wlm.set_defaults(func=_cmd_write_local_mcp)

    et = sub.add_parser("estimate-tokens")
    et.add_argument("target", nargs="?", default=None)
    et.add_argument("--text", default=None)
    et.add_argument("--path", default=None)
    et.set_defaults(func=_cmd_estimate_tokens)

    la = sub.add_parser("list-artifacts")
    la.add_argument("manifest")
    la.set_defaults(func=_cmd_list_artifacts)

    ra = sub.add_parser("read-artifact")
    ra.add_argument("manifest")
    ra.add_argument("--id", default=None)
    ra.add_argument("--kind", default=None)
    ra.add_argument("--path", default=None)
    ra.add_argument("--offset-chars", type=int, default=0)
    ra.add_argument("--max-chars", type=int, default=1200)
    ra.set_defaults(func=_cmd_read_artifact)

    sa = sub.add_parser("search-artifact")
    sa.add_argument("manifest")
    sa.add_argument("query")
    sa.add_argument("--id", default=None)
    sa.add_argument("--kind", default=None)
    sa.add_argument("--path", default=None)
    sa.add_argument("--max-hits", type=int, default=8)
    sa.set_defaults(func=_cmd_search_artifact)

    pa = sub.add_parser("preview-artifact-table")
    pa.add_argument("manifest")
    pa.add_argument("--id", default=None)
    pa.add_argument("--kind", default=None)
    pa.add_argument("--path", default=None)
    pa.add_argument("--rows", type=int, default=8)
    pa.add_argument("--columns", nargs="*", default=None)
    pa.set_defaults(func=_cmd_preview_artifact_table)

    pc = sub.add_parser("plan-context")
    pc.add_argument("manifest")
    pc.add_argument("--phase", default="triage", choices=["triage", "analysis", "editing", "report"])
    pc.add_argument("--max-tokens", type=int, default=2800)
    pc.add_argument("--query", default=None)
    pc.add_argument("--no-repo-map", action="store_true")
    pc.add_argument("-o", "--output", default=None)
    pc.set_defaults(func=_cmd_plan_context)

    eot = sub.add_parser("export-openai-tools")
    eot.add_argument("-o", "--output", default=None)
    eot.add_argument("--profile", default="starter")
    eot.add_argument("--non-strict", action="store_true")
    eot.set_defaults(func=_cmd_export_openai_tools)

    it = sub.add_parser("invoke-tool")
    it.add_argument("name")
    it.add_argument("--input-json", default=None)
    it.add_argument("--repo-root", default=None)
    it.set_defaults(func=_cmd_invoke_tool)

    sub.add_parser("mcp-server").set_defaults(func=_cmd_mcp_server)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "cmd", None) is None:
        print(render_essential_commands_markdown())
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
