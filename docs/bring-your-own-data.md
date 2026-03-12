# Bring your own data

If you already have a CSV, start here instead of the demo gallery.

`tscfbench` now has two direct Python entry points for real data:

- `run_panel_data`: one treated unit plus comparison units over time
- `run_impact_data`: one treated series plus one or more control series

CLI wrappers still exist as `run-csv-panel` and `run-csv-impact`, but the docs lead with Python because this page is for users, not agents.

## 1. Panel data: one treated unit plus donor pool

Use this when you have many units over time and exactly one treated unit.

Expected CSV shape:

```text
city,date,traffic_index
Harbor City,2024-03-01,101.2
Harbor City,2024-03-02,100.7
North City,2024-03-01,98.4
North City,2024-03-02,98.9
...
```

Required columns:

- one unit column such as `city` or `region`
- one time column such as `date` or `year`
- one outcome column such as `traffic_index` or `employment_index`

Run it in Python:

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

That writes:

- `panel_prediction_frame.csv`
- `panel_metrics.json`
- `panel_report.md`
- treated-vs-counterfactual charts
- point-effect and cumulative-impact charts

## 2. Impact data: one treated series plus controls

Use this when you have one main outcome series and one or more control series in the same table.

Expected CSV shape:

```text
date,signups,peer_signups,search_interest
2024-04-01,120,116,54
2024-04-02,123,117,53
2024-04-03,121,115,55
...
```

Required columns:

- one time column
- one outcome column
- one or more control columns

Run it in Python:

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

That writes:

- `impact_prediction_frame.csv`
- `impact_metrics.json`
- `impact_report.md`
- treated-vs-counterfactual charts
- point-effect and cumulative-impact charts

## 3. How to choose between the two

- Use `run_panel_data` when your data is naturally `unit x time`
- Use `run_impact_data` when your data is one treated series with control columns already aligned by time

## 4. Time column and intervention format

- `date` columns can be normal date strings such as `2024-07-14`
- integer-like time columns such as `year` also work
- `intervention_t` should match one value in your time column

## 5. If you still prefer CLI

Use `run-csv-panel` or `run-csv-impact` when you want copy-paste terminal commands, CI jobs, or shell scripts. They are thin wrappers around the same workflow.
