# Bring your own data

If you already have a CSV, start here instead of the demo gallery.

`tscfbench` has two direct entry points for real data:

- `run-csv-panel`: one treated unit plus comparison units over time
- `run-csv-impact`: one treated series plus one or more control series

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

Run it:

```bash
python -m tscfbench run-csv-panel my_panel.csv \
  --unit-col city \
  --time-col date \
  --y-col traffic_index \
  --treated-unit "Harbor City" \
  --intervention-t 2024-03-06 \
  --output my_panel_run
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

Run it:

```bash
python -m tscfbench run-csv-impact my_impact.csv \
  --time-col date \
  --y-col signups \
  --x-cols peer_signups search_interest \
  --intervention-t 2024-04-23 \
  --output my_impact_run
```

That writes:

- `impact_prediction_frame.csv`
- `impact_metrics.json`
- `impact_report.md`
- treated-vs-counterfactual charts
- point-effect and cumulative-impact charts

## 3. How to choose between the two

- Use `run-csv-panel` when your data is naturally `unit x time`
- Use `run-csv-impact` when your data is one treated series with control columns already aligned by time

## 4. Time column and intervention format

- `date` columns can be normal date strings such as `2024-07-14`
- integer-like time columns such as `year` also work
- `--intervention-t` should match one value in your time column

## 5. If you prefer Python instead of CLI

There is already a panel tutorial at [`docs/tutorials/custom-panel-workflow.md`](tutorials/custom-panel-workflow.md).

If the CLI path works, switch to Python only when you want to customize the workflow, not for the first successful run.
