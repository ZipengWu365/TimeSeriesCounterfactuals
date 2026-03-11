# Installation

## Recommended first run

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

## Minimal install

```bash
python -m pip install -e .
```

That path keeps the dependency surface small and still supports quickstart, reports, and SVG fallback visuals.

## Release wheel

```bash
python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib
python -m tscfbench quickstart
```

## PyPI-ready note

The project metadata in this release is prepared for `pip install tscfbench[starter]`, but this artifact snapshot is not actually published to PyPI from the current environment.
