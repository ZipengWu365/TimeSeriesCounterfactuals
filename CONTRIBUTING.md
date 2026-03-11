# Contributing to tscfbench

Thank you for contributing.

## Development workflow

```bash
pip install -e .[dev]
pytest -q
```

## Pull request expectations

- keep user-facing docs in English,
- add or update tests for protocol changes,
- prefer schema-stable JSON outputs over ad hoc text,
- document any new optional dependency in the installation matrix,
- and include at least one runnable example for major new features.

## Benchmark discipline

Do not change benchmark defaults casually. If you change a protocol-level default, explain why and update tutorial pages and canonical reports accordingly.
