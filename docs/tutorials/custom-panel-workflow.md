# Tutorial: bring your own panel data

This tutorial is for the most common applied-research question:

> I already have a panel dataset. How do I use tscfbench without rewriting my project around it?

## Step 1: make your data long-format

Your DataFrame should contain at least these columns:

- one unit column,
- one time column,
- one outcome column.

## Step 2: wrap the data in `PanelCase`

```python
from tscfbench import PanelCase

case = PanelCase(
    df=my_panel_df,
    unit_col="state",
    time_col="year",
    y_col="cigsale",
    treated_unit="California",
    intervention_t=1989,
)
```

## Step 3: choose a first model and protocol

```python
from tscfbench import PanelProtocolConfig, benchmark_panel
from tscfbench.models.synthetic_control import SimpleSyntheticControl

report = benchmark_panel(
    case,
    SimpleSyntheticControl(),
    config=PanelProtocolConfig(
        run_space_placebo=True,
        run_time_placebo=True,
        placebo_pre_rmspe_factor=5.0,
        min_pre_periods=12,
        max_time_placebos=8,
    ),
)
```

## Step 4: inspect metrics and placebo tables

```python
print(report.metrics)
print(report.space_placebos.head())
print(report.time_placebos.head())
```

## Step 5: render a Markdown report

```python
from tscfbench.report import render_panel_markdown

md = render_panel_markdown(case, report)
```

## When to move beyond this tutorial

Once this path works, the next upgrade is usually one of:

- switch to a JSON spec for reproducibility,
- run a sweep to compare multiple models,
- or wire in an external adapter.
