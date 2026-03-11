# Scenario matrix

Use this page when the question is not *what function exists?* but *what should I do in my situation?*

## You are writing a new counterfactual method paper

**Persona:** methods researcher

**Environment:** CLI + notebook + CI

**Question:** How do I compare my method against recognizable studies without wiring everything by hand?

**Where tscfbench helps**

- Gives you canonical studies other researchers already recognize.
- Lets you express sweeps as JSON specs instead of notebook state.
- Turns runs into reports that fit a paper companion or CI job.

**Primary APIs:** CanonicalBenchmarkSpec, SweepMatrixSpec, run_canonical_benchmark, run_sweep

**Primary CLI**

```bash
python -m tscfbench make-canonical-spec
python -m tscfbench make-sweep-spec
python -m tscfbench run-sweep
```

**Outputs:** canonical report, sweep report, JSON results

## You have your own panel data

**Persona:** applied researcher

**Environment:** notebook first, then script or CLI

**Question:** How do I get from my long-format panel to a placebo-aware report that collaborators can read?

**Where tscfbench helps**

- Wraps your data in a shared PanelCase schema.
- Adds placebo diagnostics and report rendering.
- Keeps exploration and reproduction aligned.

**Primary APIs:** PanelCase, benchmark_panel, PanelProtocolConfig, render_panel_markdown

**Primary CLI**

```bash
python -m tscfbench make-panel-spec
python -m tscfbench run-panel-spec
python -m tscfbench render-panel-report
```

**Outputs:** panel benchmark output, placebo tables, markdown report

## You study one treated time series

**Persona:** impact analyst

**Environment:** notebook or lightweight script

**Question:** How do I benchmark a single-series counterfactual workflow and keep it comparable to my panel work?

**Where tscfbench helps**

- Provides ImpactCase and BenchmarkOutput contracts.
- Keeps single-series analysis on the same benchmark philosophy as panel studies.
- Acts as a bridge to forecast-as-counterfactual adapters.

**Primary APIs:** ImpactCase, benchmark, OLSImpact

**Primary CLI**

```bash
python -m tscfbench demo
python -m tscfbench make-sweep-spec --task-family impact
```

**Outputs:** prediction frame, effect metrics, impact workflow demo

## You want to teach this topic

**Persona:** instructor or lab lead

**Environment:** docs site + notebooks

**Question:** How do I introduce the package without dumping source files on the audience?

**Where tscfbench helps**

- Provides a package story, benchmark cards, and tutorial order.
- Ships notebooks that mirror the docs.
- Makes the first successful run explicit.

**Primary APIs:** package_overview, workflow_recipes, render_benchmark_cards_markdown

**Primary CLI**

```bash
python -m tscfbench package-story
python -m tscfbench benchmark-cards
python -m tscfbench tutorial-index
```

**Outputs:** teaching-friendly docs, notebook reading order, public benchmark examples

## You use coding agents and care about token cost

**Persona:** research engineer

**Environment:** agent-enabled IDE or tool runtime

**Question:** How do I keep the agent useful when the benchmark has many files and large artifacts?

**Where tscfbench helps**

- Bundles runs into manifests, digests, and artifact handles.
- Provides repo maps and context plans.
- Exports tool schemas and an MCP server surface.

**Primary APIs:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools

**Primary CLI**

```bash
python -m tscfbench build-agent-bundle
python -m tscfbench plan-context
python -m tscfbench mcp-server
```

**Outputs:** manifest.json, run_digest.json, context_plan.json, tool schemas
