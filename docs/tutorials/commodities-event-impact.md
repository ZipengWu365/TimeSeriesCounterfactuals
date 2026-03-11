# Commodity event studies with FRED and gold price series

This tutorial uses **WTI**, **Brent**, and **gold** as public commodity event-study series.

## Why this case works

Commodity cases are easy to explain to broad audiences and fit naturally into counterfactual questions around macro or geopolitical shocks.

## Minimal example

```python
from tscfbench.datasets import load_fred_series, make_event_impact_case

wti = load_fred_series("DCOILWTICO")
brent = load_fred_series("DCOILBRENTEU")

case = make_event_impact_case(
    wti,
    {"brent": brent},
    intervention_t="2025-11-01",
)
```

## Notes

- Brent is often a natural control for WTI, or vice versa.
- Gold can be loaded from a CSV-like mirrored source when you want a safe-haven style case next to oil.
