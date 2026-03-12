# Quickstart

This is the single recommended first run.

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

## If you already have your own CSV

Do not start from a bundled demo. Use one of these two commands directly:

```bash
python -m tscfbench run-csv-panel my_panel.csv --unit-col city --time-col date --y-col traffic_index --treated-unit "Harbor City" --intervention-t 2024-03-06 --output my_panel_run
python -m tscfbench run-csv-impact my_impact.csv --time-col date --y-col signups --x-cols peer_signups search_interest --intervention-t 2024-04-23 --output my_impact_run
```

Full guide: [`bring-your-own-data.md`](bring-your-own-data.md)
