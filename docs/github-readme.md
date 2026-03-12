# tscfbench (v1.8.0)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Starter install](https://img.shields.io/badge/starter-install%20tested-success)
![Charts](https://img.shields.io/badge/output-chart--first-orange)
![Agents](https://img.shields.io/badge/agents-ready-purple)

**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**

![tscfbench quickstart hero](assets/hero_quickstart.png)

`tscfbench` is for the moment when a raw estimator is not enough: you want a chart, a report, a shareable package, and a machine-readable handoff under one reproducible spec.

## Python-first quickstart

```python
from tscfbench import run_demo

result = run_demo("city-traffic", output_dir="city_traffic_run")
result["summary"]
```

Start here if the package is being read by a person rather than a shell script: import one function, run one demo, and inspect the summary while charts and reports are written to `city_traffic_run/`.

## When to use this instead of a single estimator package

| If you need... | Use... |
|---|---|
| One specific estimator family and nothing else | a specialist package such as `tfcausalimpact`, `pysyncon`, `SCPI`, or `Darts` |
| One workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs | `tscfbench` |
| Something you can show a colleague or post online, not just model output | `tscfbench` |

## CLI quickstart

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

That path is the single recommended onboarding path when you want a fresh-environment smoke test with built-in backends, bundled snapshot data, and immediate chart/report/share assets.

## Use your own data

### Panel data

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

CLI equivalent:

```bash
python -m tscfbench run-csv-panel my_panel.csv --unit-col city --time-col date --y-col traffic_index --treated-unit "Harbor City" --intervention-t 2024-03-06 --output my_panel_run
```

### Impact data

```python
import pandas as pd
from tscfbench import run_impact_data

df = pd.read_csv("my_impact.csv")
result = run_impact_data(
    df,
    time_col="date",
    y_col="signups",
    x_cols=["peer_signups", "search_interest"],
    intervention_t="2024-04-23",
    output_dir="my_impact_run",
)

result["summary"]
```

CLI equivalent:

```bash
python -m tscfbench run-csv-impact my_impact.csv --time-col date --y-col signups --x-cols peer_signups search_interest --intervention-t 2024-04-23 --output my_impact_run
```

## What you get on the first run

- A canonical study spec and results JSON.
- A Markdown report that works in a clean environment.
- Treated-vs-counterfactual, cumulative-impact, and share-card visuals.
- A `summary.json` file plus generated-files metadata and a narrow next-step path.
