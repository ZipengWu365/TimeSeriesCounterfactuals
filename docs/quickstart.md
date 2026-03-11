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
