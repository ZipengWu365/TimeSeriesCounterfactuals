# Tutorial: agent workflows

## Why agent support matters

The package is designed for modern coding agents and token-aware research loops.

## Recommended turn split

- **Planning turn**: use tools, specs, installation matrix, and repo maps.
- **Execution turn**: run a benchmark or sweep and record artifacts.
- **Editing turn**: carry only a small patch-oriented context.

## Core commands

```bash
python -m tscfbench make-agent-spec -o agent_spec.json
python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir
python -m tscfbench plan-context bundle_dir/manifest.json --phase editing
```

## Why this is useful

The bundle separates compact summaries from larger artifacts so an agent does not need to read every CSV or report in full.
