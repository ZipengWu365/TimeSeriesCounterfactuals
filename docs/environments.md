# Environment guide

python -m tscfbench is intentionally usable in several environments. The right entry point depends on how formal, reproducible, and automated your workflow needs to be.

## Notebook research

**Best for:** Exploration, pedagogy, and first-pass method debugging.

**What works well here**

- Wrap your data in ImpactCase or PanelCase and inspect results interactively.
- Prototype on built-in baselines before installing heavier optional dependencies.
- Render Markdown reports once the notebook logic stabilizes.

**Recommended APIs:** ImpactCase, PanelCase, benchmark, benchmark_panel, render_panel_markdown

**Recommended CLI commands**

```bash
python -m tscfbench demo
```

**Install extras:** core

**Cautions**

- Notebook state can drift; switch to JSON specs when you want a reproducible benchmark.

## CLI-first research workflow

**Best for:** Reproducible scripts, shared repositories, and low-friction onboarding.

**What works well here**

- Create specs and reports without writing orchestration code.
- Share the same benchmark recipe across machines and collaborators.
- Use canonical studies as the public entry point for the project.

**Recommended APIs:** PanelExperimentSpec, CanonicalBenchmarkSpec, SweepMatrixSpec

**Recommended CLI commands**

```bash
python -m tscfbench make-canonical-spec
python -m tscfbench run-canonical
python -m tscfbench run-sweep
```

**Install extras:** core, research

**Cautions**

- Keep output files under version control if they are part of a paper companion or release process.

## CI and release engineering

**Best for:** Regression checks, optional-dependency smoke tests, and repeatable releases.

**What works well here**

- Use snapshot-backed canonical studies to avoid flaky network-bound tests.
- Separate core tests from optional third-party install jobs.
- Render reports as artifacts in CI for easier inspection of failures.

**Recommended APIs:** CanonicalBenchmarkSpec, run_canonical_benchmark, install_matrix

**Recommended CLI commands**

```bash
python -m tscfbench make-canonical-spec --data-source snapshot
python -m tscfbench run-canonical
```

**Install extras:** dev, research

**Cautions**

- Do not assume every optional third-party package is available on every platform; keep install tiers explicit.

## Agent-assisted coding environment

**Best for:** Token-aware research automation, code navigation, and structured tool use.

**What works well here**

- Build a small bundle and let the agent read manifest-backed artifacts on demand.
- Use function-tool or MCP exports when you want the package to explain its own surface to the agent.
- Keep large files out of chat and let context plans decide what enters the window.

**Recommended APIs:** AgentResearchTaskSpec, build_panel_agent_bundle, build_context_plan, export_openai_function_tools, TSCFBenchMCPServer

**Recommended CLI commands**

```bash
python -m tscfbench make-agent-spec
python -m tscfbench build-agent-bundle
python -m tscfbench export-openai-tools
python -m tscfbench mcp-server
```

**Install extras:** core

**Cautions**

- Separate planning turns from editing turns if you want tighter control over token usage and tool availability.

## Shared server or HPC-style batch environment

**Best for:** Larger sweeps, heavier optional models, and scheduled benchmarks.

**What works well here**

- Use sweep specs to make runs explicit and easy to rerun on another machine.
- Install only the extras you need for a given benchmark battery.
- Store JSON results and Markdown summaries as durable artifacts rather than relying on notebook state.

**Recommended APIs:** SweepMatrixSpec, run_sweep, render_sweep_markdown, install_matrix

**Recommended CLI commands**

```bash
python -m tscfbench make-sweep-spec
python -m tscfbench run-sweep
```

**Install extras:** research, forecast

**Cautions**

- Third-party deep-learning or Bayesian stacks may have platform-specific dependency constraints.

## Teaching and workshop environment

**Best for:** Live demos, student assignments, and reproducible teaching materials.

**What works well here**

- Use canonical snapshot studies so every participant sees the same results.
- Prefer the CLI and small example scripts for classrooms with mixed Python skill levels.
- Use docs pages and case studies as the main narrative surface, not only raw API references.

**Recommended APIs:** list_canonical_studies, CanonicalBenchmarkSpec, render_canonical_markdown

**Recommended CLI commands**

```bash
python -m tscfbench list-canonical-studies
python -m tscfbench run-canonical
```

**Install extras:** core

**Cautions**

- Keep classroom exercises small and deterministic; save external-package comparisons for advanced sessions.
