# Case study: German reunification

## Why this case matters

Germany is one of the most recognizable synthetic-control examples in comparative political economy. It is a natural first example because researchers immediately understand the intervention narrative.

## Study defaults in `tscfbench`

- dataset id: `german_reunification`
- treated unit: `West Germany`
- intervention year: `1990`
- outcome: `gdp`

## Suggested command

```bash
python -m tscfbench make-canonical-spec --study-ids germany --data-source snapshot --no-external -o germany.json
python -m tscfbench run-canonical germany.json -o germany_results.json
```

## Teaching tip

This case is ideal for explaining donor pools, placebo logic, and why a benchmark should separate protocol from model implementation.
