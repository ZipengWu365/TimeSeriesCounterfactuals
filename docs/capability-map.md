# Capability map

This page explains **what each part of tscfbench is for**, **why that part exists**, and **where it works best**.

## Orientation and package framing

**Question it answers:** What is this package and where should I start?

**Why this exists:** Research packages are hard to adopt when a newcomer has to reverse-engineer the repo before they can run a first result.

**Primary APIs:** package_overview, recommend_start_path, workflow_recipes

**Primary CLI commands**

```bash
python -m tscfbench intro
python -m tscfbench start-here
python -m tscfbench workflow-recipes
```

**Best environments:** docs site, CLI, teaching, notebook onboarding

**Typical outputs**

- package mental model
- recommended first path
- onboarding reading order

## Counterfactual task schema

**Question it answers:** How do I express my own data so different models and workflows share one protocol?

**Why this exists:** Counterfactual tooling is fragmented across panel, impact, and forecasting ecosystems; the schema layer keeps them interoperable.

**Primary APIs:** ImpactCase, PanelCase, PredictionResult

**Primary CLI commands**

```bash
python -m tscfbench make-panel-spec
```

**Best environments:** notebook, python script, library integration

**Typical outputs**

- validated case objects
- shared prediction contract
- JSON specs

## Single-study benchmarking

**Question it answers:** How do I run one interpretable benchmark with diagnostics instead of just a fitted curve?

**Why this exists:** Researchers need metrics, placebo logic, and readable outputs, not only predictions.

**Primary APIs:** benchmark, benchmark_panel, PanelProtocolConfig, render_panel_markdown

**Primary CLI commands**

```bash
python -m tscfbench demo
python -m tscfbench run-panel-spec
python -m tscfbench render-panel-report
```

**Best environments:** notebook, script, CLI

**Typical outputs**

- metrics
- placebo tables
- markdown report

## Canonical benchmark studies

**Question it answers:** How do I benchmark on recognizable cases that other researchers already know?

**Why this exists:** A benchmark package becomes more legible when it ships with a small number of public landmark studies.

**Primary APIs:** CanonicalBenchmarkSpec, run_canonical_benchmark, render_canonical_markdown

**Primary CLI commands**

```bash
python -m tscfbench make-canonical-spec
python -m tscfbench run-canonical
python -m tscfbench render-canonical-report
```

**Best environments:** CLI, paper companion, docs site, CI

**Typical outputs**

- canonical benchmark JSON
- cross-study report
- snapshot regression runs

## Model comparison and ecosystem planning

**Question it answers:** How do I compare built-in and external models under one protocol?

**Why this exists:** Benchmark stacks often break because dependency planning and experiment comparison live in different places.

**Primary APIs:** SweepMatrixSpec, run_sweep, adapter_catalog, install_matrix

**Primary CLI commands**

```bash
python -m tscfbench make-sweep-spec
python -m tscfbench run-sweep
python -m tscfbench install-matrix
python -m tscfbench list-adapters
```

**Best environments:** CLI, CI, shared server, methods notebook

**Typical outputs**

- sweep specs
- comparison reports
- install plans

## Teaching, tutorials, and dissemination

**Question it answers:** How do I make the package understandable to collaborators, reviewers, and students?

**Why this exists:** Good code still fails to spread if there is no public-facing package story, tutorial order, or benchmark card layer.

**Primary APIs:** render_benchmark_cards_markdown, render_workflow_recipes_markdown

**Primary CLI commands**

```bash
python -m tscfbench benchmark-cards
python -m tscfbench tutorial-index
python -m tscfbench package-story
```

**Best environments:** README, docs site, teaching, conference tutorial

**Typical outputs**

- benchmark cards
- tutorial reading order
- release-facing markdown

## Agent-native research workflows

**Question it answers:** How do I use coding agents without sending the whole repo and the whole dataset every turn?

**Why this exists:** Agent-friendly workflows need specs, bundles, handles, and context plans rather than giant free-form prompts.

**Primary APIs:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools

**Primary CLI commands**

```bash
python -m tscfbench make-agent-spec
python -m tscfbench build-agent-bundle
python -m tscfbench plan-context
python -m tscfbench export-openai-tools
```

**Best environments:** agent IDE, tool-calling runtime, CI

**Typical outputs**

- agent spec JSON
- bundle manifest
- context plan
- tool schemas
