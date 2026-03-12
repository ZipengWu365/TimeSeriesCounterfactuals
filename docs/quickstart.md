# Quickstart

Start from Python if you are learning the package as a user rather than validating a shell workflow.

## 1. Run a demo in Python

```python
from tscfbench import run_demo

result = run_demo("city-traffic", output_dir="city_traffic_run")
result["summary"]
```

That writes a report, prediction frame, metrics JSON, and chart assets into `city_traffic_run/`.

## 2. Run your own data in Python

If you already have a CSV, load it into pandas and call the package directly.

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

For single-series impact analysis, use `run_impact_data`.

## 3. Use the CLI when you want an environment smoke test

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

That path works with built-in backends and bundled snapshot data. On a starter install, it should write:

- a canonical benchmark spec
- a results JSON file
- a Markdown report
- a `summary.json` file
- treated-vs-counterfactual, cumulative-impact, and share-card visuals
- `generated_files.json`

If you are starting from a release wheel instead of a source checkout:

```bash
python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib
python -m tscfbench quickstart
```

Minimal installs still work; they fall back to SVG-only visuals when matplotlib is unavailable.

## 4. If you prefer CLI for your own CSV

```bash
python -m tscfbench run-csv-panel my_panel.csv --unit-col city --time-col date --y-col traffic_index --treated-unit "Harbor City" --intervention-t 2024-03-06 --output my_panel_run
python -m tscfbench run-csv-impact my_impact.csv --time-col date --y-col signups --x-cols peer_signups search_interest --intervention-t 2024-04-23 --output my_impact_run
```

Full guide: [`bring-your-own-data.md`](bring-your-own-data.md)
