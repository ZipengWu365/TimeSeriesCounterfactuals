# Benchmark protocol

## Guiding principle

A benchmark should compare methods under a stable protocol, not under ad hoc evaluation code.

## Panel protocol

For panel studies, `tscfbench` emphasizes:

- pre-period fit,
- post-period counterfactual gap,
- post/pre RMSPE ratio,
- space placebo comparisons,
- time placebo comparisons when enough pre-periods exist.

## Impact protocol

For impact cases with known counterfactuals or synthetic data, the package tracks:

- RMSE,
- MAE,
- cumulative effect error,
- and optional interval diagnostics.

## Canonical studies

The canonical panel benchmark uses:

- Germany,
- Prop99,
- Basque.

The same study runner can target `source=remote` or `source=snapshot`.

## Snapshot fixtures

Bundled snapshots exist for tutorials and CI. They preserve the expected schema and study identity but are intentionally lightweight so regression tests are deterministic and do not depend on external mirrors.
