# What tscfbench is

python -m tscfbench helps researchers define counterfactual benchmark tasks, run reproducible studies, compare models across panel and impact settings, and package the results for humans, CI systems, and coding agents.

## What problem it solves

- Benchmark code for time-series counterfactual inference is often rewritten from scratch and drifts across projects.
- The ecosystem is fragmented across synthetic-control, impact-analysis, and forecasting libraries with incompatible APIs.
- Research packages are often hard to teach, hard to reproduce, and hard to operationalize in CI or agent-driven coding workflows.

## What the package provides

- Canonical data containers for impact and panel counterfactual tasks.
- Single-case and multi-model benchmark runners with placebo-aware evaluation for panel studies.
- Canonical study runners for Germany, Prop99, and Basque so researchers have recognizable starting points.
- Adapter discovery, installation planning, and optional bridges to third-party ecosystems.
- JSON-first specs, Markdown reports, and agent-native bundles for token-aware workflows.

## Who it is for

- Methods researchers building or comparing new counterfactual estimators.
- Applied researchers running policy evaluation or intervention analysis on time-indexed data.
- Instructors who want stable teaching examples and snapshot-backed tutorials.
- Tool builders who need CI-friendly benchmark regressions and agent-friendly artifacts.

## What it is not

- It is not a claim that one built-in model is state of the art.
- It is not a data warehouse or experiment tracking platform.
- It is not limited to one methodological family; its job is to give them a shared protocol and workflow surface.

## Task families

### Single treated series with controls

Estimate the post-intervention counterfactual path of one outcome series and derive treatment impact.

Primary objects: ImpactCase, benchmark, OLSImpact, tfp_causalimpact

### Single treated unit in a panel

Run synthetic-control style studies with placebo diagnostics and protocol-based reporting.

Primary objects: PanelCase, benchmark_panel, PanelProtocolConfig, SimpleSyntheticControl, DifferenceInDifferences

### Benchmark operations and dissemination

Compare models across studies, generate reproducible specs, build reports, and package artifacts for CI or agents.

Primary objects: SweepMatrixSpec, CanonicalBenchmarkSpec, AgentResearchTaskSpec, build_panel_agent_bundle

## Primary outputs

- JSON specs that can be checked into git or passed to agents.
- Markdown reports for experiments, canonical studies, and sweeps.
- Artifact bundles with manifest, digest, and context-pack files for token-aware automation.
- Installation and adapter catalogs to navigate the wider ecosystem.

## First commands to run

Start narrow. You do not need the whole package surface on day one.

```bash
python -m tscfbench start-here
python -m tscfbench quickstart
python -m tscfbench doctor
python -m tscfbench essentials
```
