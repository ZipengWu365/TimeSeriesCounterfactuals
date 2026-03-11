# CLI guide

The full CLI is broad because the package covers benchmarking, reporting, packaging, and agent workflows. Most users should start with the narrow entry surface below and ignore the rest until needed.

## Narrow first-run surface

```bash
python -m tscfbench start-here
python -m tscfbench quickstart
python -m tscfbench doctor
python -m tscfbench essentials
```

## Then expand only when needed

## Understand the package

Read the package as a product: what it is, why it exists, what APIs matter, and where it fits.

**Typical user:** A new researcher, collaborator, or maintainer onboarding to the project.

```bash
python -m tscfbench intro
python -m tscfbench api-handbook
python -m tscfbench use-cases
python -m tscfbench environments
```

## Run the standard studies

Get to a recognizable panel counterfactual benchmark quickly.

**Typical user:** A researcher who wants a trusted first run or a teaching example.

```bash
python -m tscfbench list-canonical-studies
python -m tscfbench make-canonical-spec
python -m tscfbench run-canonical
python -m tscfbench render-canonical-report
```

## Compare multiple models

Build a comparison grid across models and datasets.

**Typical user:** A methods researcher or maintainer evaluating multiple adapters.

```bash
python -m tscfbench list-model-ids
python -m tscfbench make-sweep-spec
python -m tscfbench run-sweep
python -m tscfbench render-sweep-report
```

## Work with coding agents

Create small, machine-readable artifacts for tool-calling or MCP-style workflows.

**Typical user:** A research engineer using an LLM agent as part of development or analysis.

```bash
python -m tscfbench make-agent-spec
python -m tscfbench build-agent-bundle
python -m tscfbench plan-context
python -m tscfbench export-openai-tools
python -m tscfbench mcp-server
```
