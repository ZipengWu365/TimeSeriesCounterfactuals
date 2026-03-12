# tscfbench

**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**

![Quickstart hero](assets/hero_quickstart.png)

This package is easiest to understand as a **counterfactual workflow product**: it helps you go from a question to a chart, a report, and a handoff artifact without inventing a one-off workflow every time.

## First minute

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

The starter extra is the single recommended onboarding path. A release wheel is bundled with the release assets, and the package metadata is ready for PyPI publication once you push a live release.

## Why not just install one estimator?

- Use a specialist estimator when you already know the exact model family you want.
- Use `tscfbench` when you need one workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs.
- Use `tscfbench` when the deliverable matters as much as the model: chart, report, share package, and structured handoff.

## Start from your real question

### I want the fastest possible first result

- [Quickstart](quickstart.md)
- [Essential commands](essential-commands.md)
- [Doctor](doctor.md)

### I want to run my own data right now

- [Bring your own data](bring-your-own-data.md)
- [Custom panel workflow](tutorials/custom-panel-workflow.md)

### I want a demo I can show another person

- [Demo gallery](demo-gallery.md)
- [Showcase gallery](showcase-gallery.md)
- [Detector downtime tutorial](tutorials/detector-downtime.md)
- [Minimum-wage employment tutorial](tutorials/minimum-wage-employment.md)
- [Viral attention tutorial](tutorials/viral-attention.md)

### I want a no-jargon explanation

- [Plain-language guide](plain-language-guide.md)
- [Try now](try-now.md)

### I care about coding agents and token cost

- [Agent-first design](agent-first-design.md)
- [Tool profiles](tool-profiles.md)
- [Environment guide](environments.md)
