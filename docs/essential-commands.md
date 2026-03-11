# Essential commands

This page is intentionally narrow. It shows the small command set most users need before the wider research and agent surfaces.

## First 60 seconds

Use this copy-paste path when you want the most reliable first result across Linux, macOS, and Windows.

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

## Public demos people understand fast

Use these when you want a chart-first story before you think about protocols, placebos, or adapters.

```bash
python -m tscfbench demo repo-breakout
python -m tscfbench demo climate-grid
python -m tscfbench demo hospital-surge
python -m tscfbench demo detector-downtime
python -m tscfbench demo minimum-wage-employment
python -m tscfbench demo viral-attention
```

## Make something you can actually post

Use this when you want a chart, share card, short summary, and citation block that can be posted or sent to a colleague.

```bash
python -m tscfbench make-share-package --demo-id repo-breakout
python -m tscfbench make-share-package --demo-id detector-downtime
```

## Narrow agent path

Use this when you want the smallest tool surface and a bounded artifact bundle before moving to broader profiles.

```bash
python -m tscfbench export-openai-tools --profile starter -o openai_tools_starter.json
python -m tscfbench make-agent-spec -o agent_spec.json
python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir
```
