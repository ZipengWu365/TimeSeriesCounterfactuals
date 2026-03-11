# Workflow recipes

These recipes explain the package from the user's point of view: situation first, API second.

## Start by understanding the package before choosing a method

Best for new users who need a mental model of the package, its layers, and its outputs.

**Persona:** new researcher or collaborator

**Task family:** overview

**Best environment:** docs site + notebook + short CLI session

**Why this recipe exists**

Most research packages fail adoption because a newcomer cannot tell what the package is for, which layer matters, and what a successful first run should produce. This recipe fixes that first-contact problem.

**What you do**

- Read the product-level introduction and the API handbook rather than jumping straight into source files.
- Run a tiny canonical benchmark so you can see the shape of the outputs.
- Use the package tour notebook to connect concepts, CLI commands, and Python objects.

**Recommended APIs:** package_overview, api_handbook, use_case_catalog

**Recommended CLI**

```bash
python -m tscfbench start-here
python -m tscfbench intro
python -m tscfbench api-handbook
python -m tscfbench recommend-path --persona new --goal understand
```

**Recommended docs:** docs/index.md, docs/start-here.md, docs/what-is-tscfbench.md, docs/api-handbook.md

**Recommended examples:** examples/package_tour.py, examples/recommend_path_demo.py

**Recommended notebooks:** notebooks/01_start_here.ipynb, notebooks/02_package_tour.ipynb

**Expected outputs:** A clear mental model of task layer / benchmark layer / workflow layer, A first canonical JSON spec, A first Markdown report

**Notes**

- Use this recipe in workshops, onboarding docs, and when introducing the package to a new lab member.

## Run recognizable panel counterfactual studies first

Best for methods researchers or reviewers who want standard reference cases before custom data.

**Persona:** methods researcher

**Task family:** panel

**Best environment:** CLI-first workflow or reproducible notebook

**Why this recipe exists**

Germany, Prop99, and Basque are the public face of the package because they give researchers familiar landmarks and make benchmark reports immediately legible to the literature.

**What you do**

- Generate a canonical benchmark spec instead of hand-writing a one-off notebook flow.
- Run the canonical study battery on snapshot or remote data.
- Render a Markdown report that can live in a repo, paper companion, or docs site.

**Recommended APIs:** CanonicalBenchmarkSpec, run_canonical_benchmark, render_canonical_markdown

**Recommended CLI**

```bash
python -m tscfbench make-canonical-spec --data-source snapshot -o canonical.json
python -m tscfbench run-canonical canonical.json -o canonical_results.json
python -m tscfbench render-canonical-report canonical.json -o canonical_report.md
```

**Recommended docs:** docs/case-studies/germany.md, docs/case-studies/prop99.md, docs/case-studies/basque.md, docs/benchmark-cards.md

**Recommended examples:** examples/canonical_benchmark_demo.py

**Recommended notebooks:** notebooks/03_canonical_benchmark.ipynb

**Expected outputs:** canonical.json, canonical_results.json, canonical_report.md

**Notes**

- This is the most publication-friendly entry path for a new benchmark paper.

## Bring your own panel data into a placebo-aware benchmark

Best for applied researchers with their own policy or intervention panel data.

**Persona:** applied researcher

**Task family:** panel

**Best environment:** notebook for exploration, then Python script or CLI for reproduction

**Why this recipe exists**

Researchers often have panel data ready to go but no stable way to impose placebo checks, consistent outputs, and a benchmark protocol. This recipe provides that bridge.

**What you do**

- Wrap your long-format panel in PanelCase.
- Select a baseline or adapter and run benchmark_panel under a fixed protocol.
- Inspect placebo diagnostics and render a Markdown report for collaborators.

**Recommended APIs:** PanelCase, benchmark_panel, PanelProtocolConfig, render_panel_markdown

**Recommended CLI**

```bash
python -m tscfbench make-panel-spec --dataset synthetic_latent_factor -o panel.json
python -m tscfbench run-panel-spec panel.json
python -m tscfbench render-panel-report panel.json -o panel_report.md
```

**Recommended docs:** docs/tutorials/custom-panel-workflow.md, docs/use-cases.md, docs/environments.md

**Recommended examples:** examples/custom_panel_data_demo.py, examples/panel_research_demo.py

**Recommended notebooks:** notebooks/04_custom_panel_data.ipynb

**Expected outputs:** PanelBenchmarkOutput, placebo tables, panel_report.md

**Notes**

- Use this path when the scientific question is applied and the workflow needs to stay readable for collaborators.

## Benchmark one treated time series with controls

Best for intervention analysis, product analytics, or forecast-as-counterfactual workflows.

**Persona:** impact analyst

**Task family:** impact

**Best environment:** notebook or lightweight script

**Why this recipe exists**

Time-series counterfactual work is not only synthetic control. This recipe gives a single-series path with controls, predictive counterfactuals, and effect error metrics.

**What you do**

- Define an ImpactCase with pre/post intervention periods and any controls.
- Run benchmark on a built-in baseline or an external impact adapter.
- Examine counterfactual error, effect-path error, and cumulative effect summaries.

**Recommended APIs:** ImpactCase, benchmark, OLSImpact

**Recommended CLI**

```bash
python -m tscfbench demo
python -m tscfbench list-model-ids --task-family impact
python -m tscfbench make-sweep-spec --task-family impact -o impact_sweep.json
```

**Recommended docs:** docs/use-cases.md, docs/api-handbook.md, docs/benchmark-cards.md

**Recommended examples:** examples/package_tour.py

**Recommended notebooks:** notebooks/06_impact_workflow.ipynb

**Expected outputs:** BenchmarkOutput, prediction frame, impact metrics

**Notes**

- This path is the most natural bridge to forecast-as-counterfactual adapters such as TFT-style workflows.

## Run a multi-model sweep for a methods paper

Best for researchers comparing several models or adapters under one protocol.

**Persona:** methods researcher

**Task family:** research_ops

**Best environment:** CLI + CI + structured reports

**Why this recipe exists**

A paper-grade benchmark needs more than a single run. This recipe standardizes sweep matrices, error-tolerant execution, and comparison reports so experiments stay reproducible.

**What you do**

- Create a sweep spec that lists studies, models, and data source choices.
- Run the sweep with cell-level error tolerance for optional dependencies.
- Render a compact comparison report and store the JSON results for regression testing.

**Recommended APIs:** SweepMatrixSpec, run_sweep, render_sweep_markdown

**Recommended CLI**

```bash
python -m tscfbench make-sweep-spec --task-family panel -o panel_sweep.json
python -m tscfbench run-sweep panel_sweep.json -o panel_results.json
python -m tscfbench render-sweep-report panel_sweep.json -o panel_report.md
```

**Recommended docs:** docs/benchmark-protocol.md, docs/cli-guide.md, docs/workflow-recipes.md

**Recommended examples:** examples/panel_research_demo.py

**Recommended notebooks:** notebooks/07_method_paper_sweep.ipynb

**Expected outputs:** panel_sweep.json, panel_results.json, panel_report.md

**Notes**

- This is the path most likely to land in a benchmark appendix, CI regression suite, or paper companion repo.

## Use coding agents without blowing up token usage

Best for research engineers using MCP, function calling, or agent-enabled IDEs.

**Persona:** research engineer

**Task family:** research_ops

**Best environment:** agent-enabled IDE or tool-calling runtime

**Why this recipe exists**

Large benchmark artifacts are awkward in chat and IDE agents. This recipe packages experiments into specs, digests, repo maps, and bounded artifact handles so an agent can reason without seeing the whole dataset.

**What you do**

- Create a compact research task spec instead of describing the entire task in free-form text.
- Build an artifact bundle with manifest, digest, context plan, and optional repo map.
- Use function tools or MCP to fetch only the artifact slices you actually need in context.

**Recommended APIs:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools

**Recommended CLI**

```bash
python -m tscfbench make-agent-spec -o agent_spec.json
python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir
python -m tscfbench plan-context bundle_dir/manifest.json --phase editing
```

**Recommended docs:** docs/tutorials/agent-workflows.md, docs/environments.md, docs/workflow-recipes.md

**Recommended examples:** examples/agent_bundle_demo.py, examples/openai_function_tools_demo.py, examples/mcp_roundtrip_demo.py

**Recommended notebooks:** notebooks/05_agent_workflow.ipynb

**Expected outputs:** agent_spec.json, bundle_dir/manifest.json, context_plan.json, OpenAI function-tool schemas

**Notes**

- This path is explicitly designed for token-aware, agent-driven research engineering.
