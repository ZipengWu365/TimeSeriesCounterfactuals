# API handbook

This page organizes the package by *jobs* rather than by source files. Each section explains why that API layer exists, when to use it, and what it returns.

## Core data model

**Layer:** foundation

**Entry points:** ImpactCase, PanelCase, PredictionResult

**Why this API exists**

This layer exists because most counterfactual libraries encode data differently. tscfbench needs a small, stable schema that lets the same benchmark protocol work with built-in models, external adapters, and custom user data.

**When to use it**

Use these classes whenever you want to bring your own dataset into the package or write a new model adapter.

**What it returns**

- Validated case objects with explicit intervention boundaries.
- PredictionResult objects with counterfactual path, effect path, and optional intervals.

**Works well in:** notebook, python script, library integration, teaching

**Notes**

- ImpactCase is for one treated series plus controls/covariates.
- PanelCase is for one treated unit in a long-format panel.
- PredictionResult is the common output contract for all model wrappers.

## Single-case benchmarking

**Layer:** benchmark protocol

**Entry points:** benchmark, benchmark_panel, PanelProtocolConfig

**Why this API exists**

Researchers usually need more than raw predictions: they need comparable metrics and, in panel studies, placebo-based diagnostics. This layer turns one model + one case into a protocol-aware result object.

**When to use it**

Use this when you have one case and one model and want an interpretable benchmark result quickly.

**What it returns**

- Point metrics such as RMSE, MAE, R², and cumulative-effect error for synthetic tasks.
- Panel diagnostics such as pre/post RMSPE style summaries and placebo tables.

**Works well in:** notebook, python script, quick experiment, teaching

**CLI counterparts**

```bash
python -m tscfbench demo
python -m tscfbench make-panel-spec
python -m tscfbench run-panel-spec
```

**Notes**

- benchmark() is the generic entry point for cases with ground-truth counterfactuals.
- benchmark_panel() adds panel-specific placebo logic and reporting metadata.

## Experiment specs and reproducibility

**Layer:** experiment definition

**Entry points:** PanelExperimentSpec, ImpactExperimentSpec, run_panel_experiment

**Why this API exists**

Once a benchmark leaves a notebook, ad hoc parameter passing becomes fragile. The spec layer exists so experiments can be serialized, versioned, diffed, and rerun by humans, CI jobs, or agents.

**When to use it**

Use this layer when you want JSON-first reproducibility or when you want CLI and Python workflows to mirror each other.

**What it returns**

- Serializable experiment specifications.
- Protocol outputs that can be rendered into Markdown or packed into bundles.

**Works well in:** CLI, git-based collaboration, CI, agent workflows

**CLI counterparts**

```bash
python -m tscfbench make-panel-spec
python -m tscfbench run-panel-spec
python -m tscfbench render-panel-report
```

**Notes**

- This is the best entry point for people who want reproducible experiments without writing lots of orchestration code.

## Canonical benchmark studies

**Layer:** research benchmarks

**Entry points:** list_canonical_studies, CanonicalBenchmarkSpec, run_canonical_benchmark, render_canonical_markdown

**Why this API exists**

A benchmark package becomes easier to trust and teach when it offers a small set of recognizable studies. This layer is the package's public face for empirical panel counterfactual benchmarking.

**When to use it**

Use this layer when you want a standard study battery rather than a single custom case.

**What it returns**

- A study catalog with Germany, Prop99, and Basque metadata.
- Cross-study benchmark runs and a shareable Markdown report.

**Works well in:** paper companion, tutorials, teaching, benchmark release

**CLI counterparts**

```bash
python -m tscfbench list-canonical-studies
python -m tscfbench make-canonical-spec
python -m tscfbench run-canonical
python -m tscfbench render-canonical-report
```

**Notes**

- Use snapshot mode for reproducible tutorials and CI.
- Use auto/remote mode when you want fuller study data in normal research runs.

## Model discovery and ecosystem planning

**Layer:** ecosystem navigation

**Entry points:** install_matrix, adapter_catalog, recommend_adapter_stack, list_model_ids

**Why this API exists**

Researchers rarely know up front which package stack is easiest to install, easiest to explain, or most suitable for a given task family. This layer exists to make that choice explicit rather than tribal knowledge.

**When to use it**

Use this layer before you commit to a benchmark stack or when you need to explain optional dependencies to users.

**What it returns**

- Structured install metadata and import/package names.
- Adapter cards that describe strengths, caveats, and runtime characteristics.
- Recommendations for a small, research-oriented starting stack.

**Works well in:** package maintenance, onboarding, teaching, agent planning

**CLI counterparts**

```bash
python -m tscfbench install-matrix
python -m tscfbench list-adapters
python -m tscfbench recommend-stack
python -m tscfbench list-model-ids
```

**Notes**

- This layer is especially useful when your audience is global and needs a clearer install story.

## Sweep studies and comparison grids

**Layer:** multi-run orchestration

**Entry points:** SweepMatrixSpec, make_default_sweep_spec, run_sweep, render_sweep_markdown

**Why this API exists**

Researchers often compare several model/dataset combinations at once. The sweep layer exists so those comparisons are explicit, machine-readable, and robust to partial adapter failures.

**When to use it**

Use this layer when you are comparing multiple models, datasets, or backends in a single benchmark run.

**What it returns**

- Per-cell results with success/error status.
- Comparison tables and study-level summaries.

**Works well in:** benchmarking, CI, method comparison, release validation

**CLI counterparts**

```bash
python -m tscfbench make-sweep-spec
python -m tscfbench run-sweep
python -m tscfbench render-sweep-report
```

**Notes**

- External-package failures are recorded as cell-level errors rather than crashing the full sweep by default.

## Agent-native workflow layer

**Layer:** automation

**Entry points:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools, TSCFBenchMCPServer

**Why this API exists**

Agent workflows need smaller, more structured artifacts than notebook-centric research code. This layer exists to turn benchmark runs into token-bounded specs, manifests, digests, and tool surfaces.

**When to use it**

Use this layer when a coding agent or tool-calling runtime participates in your research workflow.

**What it returns**

- Compact JSON specs and bundles.
- Repo maps, context plans, and manifest-based artifact access.
- Function-tool and MCP surfaces so the package can explain itself to agents.

**Works well in:** Cursor/Codex/ChatGPT, tool-calling backends, CI automation, multi-step research assistants

**CLI counterparts**

```bash
python -m tscfbench make-agent-spec
python -m tscfbench build-agent-bundle
python -m tscfbench plan-context
python -m tscfbench export-openai-tools
python -m tscfbench mcp-server
```

**Notes**

- This layer matters when you want lower token usage, smaller context windows, and resumable research tasks.

## Reports, teaching surfaces, and project communication

**Layer:** dissemination

**Entry points:** render_panel_markdown, render_sweep_markdown, render_canonical_markdown

**Why this API exists**

A benchmark package spreads only if the outputs are understandable outside the codebase. This layer exists so results can become readable artifacts for papers, tutorials, internal memos, and classrooms.

**When to use it**

Use this layer whenever you need a human-readable output rather than raw Python objects.

**What it returns**

- Markdown reports that summarize configuration, metrics, and comparison tables.
- A cleaner handoff from computation to writing or teaching.

**Works well in:** paper writing, teaching, project website, release notes

**CLI counterparts**

```bash
python -m tscfbench render-panel-report
python -m tscfbench render-sweep-report
python -m tscfbench render-canonical-report
```

**Notes**

- These renderers are intentionally simple so they are easy to diff and easy to post-process.
