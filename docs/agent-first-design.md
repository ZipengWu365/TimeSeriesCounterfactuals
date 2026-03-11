# Agent-first design

`tscfbench` is designed for researchers who increasingly work through coding agents, tool-calling runtimes, or editor agents.

## Design principles

- **Spec-first.** Prefer JSON specs over long free-form prompts.
- **Bundle-first.** Materialize manifests, digests, and artifact handles for each run.
- **Handle-first.** Read only the artifact slices you need.
- **Turn separation.** Keep planning/retrieval turns separate from compact editing turns.
- **Docs as tools.** Expose package explanation and comparison surfaces through CLI and tool schemas, not only prose.

## What that means in practice

- `build-agent-bundle` writes a manifest, digest, context pack, and artifacts.
- `plan-context` assembles a bounded context plan for triage, analysis, editing, or reporting.
- `repo-map` gives agents a compact structural view of the repository.
- `export-openai-tools` and `mcp-server` expose the package as a tool surface.

## Why this should save tokens

- Stable instructions and stable tool lists are easier to cache.
- Small artifact previews are cheaper than full data dumps.
- Editing turns work better when they only see the necessary files and diffs.
