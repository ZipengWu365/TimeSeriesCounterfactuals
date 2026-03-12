# Start here

**tscfbench** helps you answer a before/after question with a counterfactual, compare methods under one recipe, and save the result as a report plus agent-ready files.

In plain language: give the package one treated series or one treated unit, and it helps you build the comparison, run the study, and save outputs you can read, share, or hand to an agent.

## If you only do one thing

Start from Python so the package looks like a library rather than a terminal wrapper.

```python
from tscfbench import run_demo

result = run_demo("city-traffic", output_dir="city_traffic_run")
result["summary"]
```

That is the cleanest first contact: import, run, inspect the summary, then open the generated chart and report.

If you want a fresh-environment smoke test after that, the CLI quickstart still works:

```bash
python -m tscfbench quickstart
```

That command writes a spec, results JSON, report, next-steps file, and, when plotting support is available, a shareable chart into `tscfbench_quickstart/`.

## If you want a more human, domain-first example

Start with one of the cross-disciplinary demos. They are easier to read if words like placebo, donor pool, or synthetic control are still unfamiliar.

```python
from tscfbench import run_demo

run_demo("city-traffic", output_dir="city_traffic_run")
run_demo("product-launch", output_dir="product_launch_run")
run_demo("heatwave-health", output_dir="heatwave_health_run")
```

## If you already have your own CSV

Use the DataFrame-friendly helpers first.

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
)
```

Read [`bring-your-own-data.md`](bring-your-own-data.md) if you want both the Python and CLI shapes side by side.

## What should you do after that?

The default recommendation starts with package orientation and then moves into a canonical benchmark, because that is the lowest-friction path for most new users.

### Recommended next path: Run recognizable panel counterfactual studies first

Best for methods researchers or reviewers who want standard reference cases before custom data.

**Best environment:** CLI-first workflow or reproducible notebook

**Why this path exists**

Germany, Prop99, and Basque are the public face of the package because they give researchers familiar landmarks and make benchmark reports immediately legible to the literature.

**What you do in this path**

- Generate a canonical benchmark spec instead of hand-writing a one-off notebook flow.
- Run the canonical study battery on snapshot or remote data.
- Render a Markdown report that can live in a repo, paper companion, or docs site.

**Start with these CLI commands**

```bash
python -m tscfbench doctor
python -m tscfbench make-canonical-spec --data-source snapshot -o canonical.json
python -m tscfbench run-canonical canonical.json -o canonical_results.json
python -m tscfbench render-canonical-report canonical.json -o canonical_report.md
```

**Then read / open**

- docs/api-handbook.md
- docs/benchmark-cards.md
- docs/case-studies/basque.md
- docs/case-studies/germany.md
- docs/case-studies/prop99.md
- docs/environments.md
- docs/tutorials/custom-panel-workflow.md
- docs/use-cases.md

**Useful notebooks**

- notebooks/03_canonical_benchmark.ipynb
- notebooks/04_custom_panel_data.ipynb
- notebooks/06_impact_workflow.ipynb

## Common first paths

| Situation | Start with | Main deliverable |
|---|---|---|
| I am new to the package | quickstart | zero-error canonical starter run |
| I want standard public benchmarks | canonical-panel-studies | canonical report |
| I have my own panel data | custom-panel-data | placebo-aware panel report |
| I work on a single treated series | impact-analysis | impact metrics + prediction frame |
| I need many models / many studies | method-paper-sweep | sweep JSON + comparison report |
| I work with coding agents | agent-assisted-research | bundle + context plan + tools |

## One important note

Optional backends are useful, but they are not required for the first run. When you explicitly ask for them and they are not installed, the benchmark should mark them as skipped optional dependencies rather than looking broken.
