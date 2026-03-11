# Use cases

The fastest way to understand tscfbench is to start from your situation rather than from the internal module tree.

## You are developing a new synthetic-control or counterfactual method

**Persona:** methods researcher

**Question:** How do I compare my method against common baselines and canonical studies without inventing a benchmark from scratch?

**Best environment:** Python script + CLI + optional CI

**What tscfbench does for you**

- Gives you canonical studies and built-in baselines so you can define a first comparison grid immediately.
- Lets you express your benchmark as JSON specs and sweep matrices rather than one-off notebook state.
- Produces Markdown reports that are easy to attach to a repo or paper companion.

**Recommended entry points:** CanonicalBenchmarkSpec, SweepMatrixSpec, run_sweep, render_sweep_markdown

**Typical outputs:** canonical_results.json, panel_report.md, sweep_report.md

**Notes**

- This is the package's most research-native use case.

## You have your own policy or intervention panel data

**Persona:** applied empirical researcher

**Question:** How do I plug my own long-format panel into a benchmark protocol with placebo diagnostics?

**Best environment:** Notebook or Python script

**What tscfbench does for you**

- Lets you wrap your data in PanelCase and evaluate models under a consistent panel protocol.
- Provides simple SCM and DiD baselines even before you wire in external research packages.
- Keeps reporting logic separate from data preparation so your applied workflow stays readable.

**Recommended entry points:** PanelCase, benchmark_panel, PanelProtocolConfig, render_panel_markdown

**Typical outputs:** PanelBenchmarkOutput, placebo tables, panel Markdown report

## You are studying one treated time series with controls

**Persona:** impact analyst

**Question:** How do I benchmark impact-analysis models and compare forecast-style counterfactuals with causal-impact style baselines?

**Best environment:** Notebook, script, or product analytics workflow

**What tscfbench does for you**

- Lets you formalize a single-series counterfactual task with ImpactCase.
- Provides a built-in OLS impact baseline and room for external impact adapters.
- Measures both predictive counterfactual error and cumulative effect error when ground truth exists.

**Recommended entry points:** ImpactCase, benchmark, OLSImpact, list_model_ids(task_family='impact')

**Typical outputs:** BenchmarkOutput, prediction frame, impact metrics

## You need a stable teaching surface for a methods class

**Persona:** instructor or teaching assistant

**Question:** How can I teach canonical counterfactual case studies without depending on live downloads or fragile notebooks?

**Best environment:** Notebook, classroom laptops, offline lab, teaching repo

**What tscfbench does for you**

- Ships snapshot-compatible canonical studies for deterministic classroom runs.
- Offers a small CLI so students can reproduce the same steps with less setup friction.
- Separates the conceptual layers of the package so you can teach data schema, protocol, and model choice independently.

**Recommended entry points:** list_canonical_studies, make-canonical-spec, run-canonical, docs/case-studies

**Typical outputs:** snapshot-backed reports, case-study tutorials, repeatable teaching examples

## You want CI regression tests for benchmark behavior

**Persona:** package maintainer

**Question:** How do I make sure a change to my library does not silently break a canonical study or the reporting protocol?

**Best environment:** GitHub Actions or other CI

**What tscfbench does for you**

- Provides snapshot data sources so tests do not depend on network access.
- Lets you encode a canonical benchmark or sweep as JSON and compare outputs over time.
- Supports installation matrices so CI jobs can separate core coverage from optional dependency coverage.

**Recommended entry points:** CanonicalBenchmarkSpec, SweepMatrixSpec, install_matrix, tests/

**Typical outputs:** deterministic CI runs, snapshot results, release-ready benchmark artifacts

## You want coding agents to help with benchmark development without wasting context window

**Persona:** research engineer using coding agents

**Question:** How can I let an agent inspect experiments, reports, and datasets without pasting huge files into chat?

**Best environment:** Agent-enabled IDE, MCP client, tool-calling runtime

**What tscfbench does for you**

- Builds compact task specs, bundles, digests, repo maps, and context plans.
- Exposes a tool surface so an agent can ask for the install matrix, canonical studies, or artifact slices directly.
- Lets you keep large tables as artifacts and bring only the needed slices into context.

**Recommended entry points:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools

**Typical outputs:** bundle_dir/manifest.json, context_plan.json, tool-calling schemas
