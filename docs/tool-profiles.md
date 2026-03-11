# Tool profiles

Do not start by dumping the whole tool catalog into context.

Use `starter` for onboarding and the first successful run. Promote to `minimal` or `research` only when you need canonical studies, agent bundles, or bounded artifact reads. Keep `full` for MCP servers, docs generation, or deep automation.

## starter

Narrowest possible onboarding surface for quickstart, one named demo, and one share package.

- tool_count: 6
- approx_tokens: 585
- recommended_for: first run, broad users, very tight token budgets
- aliases: default, onboarding, beginner

Included tools:

- `tscf_start_here`
- `tscf_doctor`
- `tscf_run_quickstart`
- `tscf_list_demo_cases`
- `tscf_run_demo`
- `tscf_make_share_package`

## minimal

Starter-plus surface for quickstart, one named demo, a share package, and a compact agent handoff.

- tool_count: 9
- approx_tokens: 1348
- recommended_for: first successful run plus a bounded handoff to agents
- aliases: compact, narrow

Included tools:

- `tscf_start_here`
- `tscf_doctor`
- `tscf_run_quickstart`
- `tscf_make_canonical_spec`
- `tscf_list_demo_cases`
- `tscf_run_demo`
- `tscf_make_share_package`
- `tscf_make_agent_spec`
- `tscf_build_agent_bundle`

## research

Balanced research surface for canonical studies, sweeps, adapters, demos, and bounded artifact reads.

- tool_count: 19
- approx_tokens: 2279
- recommended_for: research engineers and methods users after the first successful run
- aliases: agent, balanced

Included tools:

- `tscf_start_here`
- `tscf_doctor`
- `tscf_list_canonical_studies`
- `tscf_make_canonical_spec`
- `tscf_run_canonical`
- `tscf_list_adapters`
- `tscf_recommend_stack`
- `tscf_list_model_ids`
- `tscf_make_sweep_spec`
- `tscf_run_sweep`
- `tscf_list_demo_cases`
- `tscf_run_demo`
- `tscf_make_share_package`
- `tscf_export_runtime_profile`
- `tscf_make_agent_spec`
- `tscf_build_agent_bundle`
- `tscf_list_artifacts`
- `tscf_read_artifact`
- `tscf_plan_context`

## full

Complete tool surface for full package introspection, docs generation, release assets, and deep automation.

- tool_count: 52
- approx_tokens: 9113
- recommended_for: full MCP servers and deep integrations
- aliases: all, complete

Included tools:

- `tscf_package_overview`
- `tscf_api_handbook`
- `tscf_use_case_catalog`
- `tscf_environment_profiles`
- `tscf_cli_guide`
- `tscf_package_story`
- `tscf_capability_map`
- `tscf_api_atlas`
- `tscf_scenario_matrix`
- `tscf_tutorial_index`
- `tscf_start_here`
- `tscf_workflow_recipes`
- `tscf_benchmark_cards`
- `tscf_high_traffic_cases`
- `tscf_public_data_sources`
- `tscf_ecosystem_audit`
- `tscf_feature_coverage`
- `tscf_differentiators`
- `tscf_github_readme`
- `tscf_website_home`
- `tscf_agent_first_design`
- `tscf_recommend_path`
- `tscf_list_datasets`
- `tscf_install_matrix`
- `tscf_list_canonical_studies`
- `tscf_make_canonical_spec`
- `tscf_run_canonical`
- `tscf_list_adapters`
- `tscf_recommend_stack`
- `tscf_list_model_ids`
- `tscf_make_sweep_spec`
- `tscf_run_sweep`
- `tscf_list_runtime_profiles`
- `tscf_export_runtime_profile`
- `tscf_make_agent_spec`
- `tscf_make_study_blueprint`
- `tscf_build_agent_bundle`
- `tscf_run_panel_experiment`
- `tscf_repo_map`
- `tscf_list_artifacts`
- `tscf_read_artifact`
- `tscf_search_artifact`
- `tscf_preview_artifact_table`
- `tscf_plan_context`
- `tscf_write_agents_md`
- `tscf_make_release_kit`
- `tscf_make_positioning_assets`
- `tscf_doctor`
- `tscf_run_quickstart`
- `tscf_list_demo_cases`
- `tscf_run_demo`
- `tscf_make_share_package`
