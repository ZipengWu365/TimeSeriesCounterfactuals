# Case study: Basque Country terrorism

## Why this case matters

Basque is historically central to the synthetic-control literature and is useful when discussing how comparative-case methods interact with historical shocks.

## Study defaults in `tscfbench`

- dataset id: `basque_country`
- treated unit: `Basque Country (Pais Vasco)`
- intervention year: `1970`
- outcome: `gdpcap`

## Suggested command

```bash
python -m tscfbench make-canonical-spec --study-ids basque --data-source snapshot --no-external -o basque.json
python -m tscfbench run-canonical basque.json -o basque_results.json
```

## Teaching tip

Use Basque when you want to connect the benchmark to the historical origins of SCM and discuss robustness across canonical studies rather than a single headline example.
