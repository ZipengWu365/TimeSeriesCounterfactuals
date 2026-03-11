# Tutorial: your first canonical benchmark

## Goal

Run a complete benchmark over the three canonical panel studies using bundled snapshots.

## Step 1: create a spec

```bash
python -m tscfbench make-canonical-spec --data-source snapshot --no-external -o canonical.json
```

## Step 2: run the benchmark

```bash
python -m tscfbench run-canonical canonical.json -o canonical_results.json
```

## Step 3: render the report

```bash
python -m tscfbench render-canonical-report canonical.json -o canonical_report.md
```

## What to inspect

- whether the treated unit and intervention year are correct,
- whether the pre-period fit is acceptable,
- whether placebo p-values are informative,
- whether one model dominates across all studies or only on one dataset.

## Next step

Swap `--data-source snapshot` for `--data-source auto` when you are ready to try remote mirrors.
