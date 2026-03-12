# tscfbench

**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**

![Quickstart hero](assets/hero_quickstart.png)

This package is easiest to understand as a **counterfactual workflow product**: it helps you go from a question to a chart, a report, and a handoff artifact without inventing a one-off workflow every time.

## Start in Python

```python
from tscfbench import run_demo

result = run_demo("city-traffic", output_dir="city_traffic_run")
result["summary"]
```

This is the shortest human-facing example: import the package, run one function, and open the generated chart/report assets in `city_traffic_run/`.

## Bring your own data in Python

```python
import pandas as pd
from tscfbench import run_panel_data

df = pd.read_csv("my_panel.csv")
result = run_panel_data(
    df,
    unit_col="city",
    time_col="date",
    y_col="traffic_index",
    treated_unit="Harbor City",
    intervention_t="2024-03-06",
    output_dir="my_panel_run",
)

result["summary"]
```

If your question is one treated series with controls instead of one treated unit with donor units, switch to `run_impact_data`. The full walkthrough is [Bring your own data](bring-your-own-data.md).

## CLI quickstart

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

Use the CLI when you want the narrow install smoke test in a fresh environment.

## Why not just install one estimator?

- Use a specialist estimator when you already know the exact model family you want.
- Use `tscfbench` when you need one workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs.
- Use `tscfbench` when the deliverable matters as much as the model: chart, report, share package, and structured handoff.

## Start from your real question

### I want the fastest possible first result

- [Quickstart](quickstart.md)
- [Bring your own data](bring-your-own-data.md)
- [Essential commands](essential-commands.md)
- [Doctor](doctor.md)

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
